import os
import shutil
from uuid import uuid4
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from app.database.connection import get_database
from app.api.deps import get_current_admin_user
from app.schemas.user import UserResponse
from app.models.product import get_product, update_product
from app.schemas.product import ProductUpdate

router = APIRouter()

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@router.post("/products/{product_id}/images", status_code=201)
async def upload_product_image(
    product_id: str,
    file: UploadFile = File(...),
    db = Depends(get_database),
    current_admin: UserResponse = Depends(get_current_admin_user)
):
    """
    Upload an image for a product. (Admin only)
    """
    product = await get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPG, PNG, and WEBP are allowed.")

    # Generate a unique filename
    ext = file.filename.rsplit(".", 1)[1].lower()
    unique_filename = f"{uuid4().hex}.{ext}"
    file_path = os.path.join("uploads", unique_filename)

    # Save the file
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB.")

    with open(file_path, "wb") as buffer:
        buffer.write(content)

    # Update product images array
    images = product.get("images", [])
    image_url = f"/static/{unique_filename}"
    images.append(image_url)

    await update_product(db, product_id, ProductUpdate(images=images))

    return {"filename": unique_filename, "url": image_url}

@router.delete("/products/{product_id}/images/{filename}")
async def delete_product_image(
    product_id: str,
    filename: str,
    db = Depends(get_database),
    current_admin: UserResponse = Depends(get_current_admin_user)
):
    """
    Delete a product image. (Admin only)
    """
    from bson.errors import InvalidId
    try:
        product = await get_product(db, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        image_url = f"/static/{filename}"
        images = product.get("images", [])

        if image_url not in images:
            raise HTTPException(status_code=404, detail="Image not associated with this product")

        # Remove from product images array
        images.remove(image_url)
        await update_product(db, product_id, ProductUpdate(images=images))

        # Try to delete from local uploads directory
        file_path = os.path.join("uploads", filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass  # Keep going if file can't be deleted from disk

        return {"message": "Image deleted successfully"}
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Product ID")

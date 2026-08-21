from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from bson.errors import InvalidId

from app.database.connection import get_database
from app.api.deps import get_current_admin_user
from app.schemas.user import UserResponse
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse,
    CategoryCreate, CategoryResponse
)
from app.models.product import (
    create_product, get_products, get_product, update_product, delete_product,
    create_category, get_categories, get_category
)

router = APIRouter()

# --- Categories ---

@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_new_category(
    category_in: CategoryCreate,
    db = Depends(get_database),
    current_admin: UserResponse = Depends(get_current_admin_user)
):
    """
    Create new category (Admin only).
    """
    category = await create_category(db, category_in)
    return category

@router.get("/categories", response_model=List[CategoryResponse])
async def read_categories(
    db = Depends(get_database),
    current_admin: UserResponse = Depends(get_current_admin_user)
):
    """
    Retrieve categories (Admin view).
    """
    return await get_categories(db)

@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def read_category(
    category_id: str,
    db = Depends(get_database),
    current_admin: UserResponse = Depends(get_current_admin_user)
):
    """
    Retrieve a specific category (Admin only).
    """
    try:
        category = await get_category(db, category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Category ID")

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_category(
    category_id: str,
    db = Depends(get_database),
    current_admin: UserResponse = Depends(get_current_admin_user)
):
    """
    Delete a category (Admin only).
    """
    try:
        category = await get_category(db, category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
            
        # Verify no products belong to this category
        product_count = await db.products.count_documents({"category_id": category_id})
        if product_count > 0:
            raise HTTPException(status_code=400, detail="Cannot delete category containing products")
            
        await db.categories.delete_one({"_id": ObjectId(category_id)})
        return None
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Category ID")


# --- Products ---

@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_new_product(
    product_in: ProductCreate,
    db = Depends(get_database),
    current_admin: UserResponse = Depends(get_current_admin_user)
):
    """
    Create new product (Admin only).
    """
    try:
        # Check if category exists
        category = await get_category(db, product_in.category_id)
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")
            
        product = await create_product(db, product_in=product_in, admin_id=str(current_admin.id))
        return product
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Category ID")

@router.get("/products", response_model=List[ProductResponse])
async def read_products(
    skip: int = 0,
    limit: int = 100,
    db = Depends(get_database),
    current_admin: UserResponse = Depends(get_current_admin_user)
):
    """
    Retrieve products (Admin view).
    """
    products = await get_products(db, skip=skip, limit=limit)
    return products

@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_existing_product(
    product_id: str,
    product_in: ProductUpdate,
    db = Depends(get_database),
    current_admin: UserResponse = Depends(get_current_admin_user)
):
    """
    Update a product (Admin only).
    """
    try:
        product = await get_product(db, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
            
        updated_product = await update_product(db, product_id, product_in)
        return updated_product
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Product ID")

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_product(
    product_id: str,
    db = Depends(get_database),
    current_admin: UserResponse = Depends(get_current_admin_user)
):
    """
    Delete a product (Admin only).
    """
    try:
        product = await get_product(db, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
            
        await delete_product(db, product_id)
        return None
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Product ID")

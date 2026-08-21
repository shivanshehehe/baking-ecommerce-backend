from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from bson.errors import InvalidId

from app.database.connection import get_database
from app.api.deps import get_current_user, get_current_admin_user
from app.schemas.user import UserResponse
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse
from app.models.review import create_review, get_reviews_for_product, get_review, update_review, delete_review
from app.models.product import get_product
from app.models.order import get_user_orders

router = APIRouter()

@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def add_review(
    review_in: ReviewCreate,
    db = Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Add a review for a product. Must have purchased the product.
    """
    try:
        product = await get_product(db, review_in.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Business rule: Can only review purchased products
        orders = await get_user_orders(db, user_id=str(current_user.id))
        has_purchased = False
        for order in orders:
            for item in order["order_items"]:
                if item["product_id"] == review_in.product_id:
                    has_purchased = True
                    break
            if has_purchased:
                break
                
        if not has_purchased and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="You can only review products you have purchased")

        review = await create_review(db, user_id=str(current_user.id), review_in=review_in)
        return review
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Product ID")

@router.get("/admin/all", response_model=List[ReviewResponse])
async def read_all_reviews_admin(
    skip: int = 0,
    limit: int = 100,
    db = Depends(get_database),
    current_admin: UserResponse = Depends(get_current_admin_user)
):
    """
    Retrieve all reviews in the system for moderation (Admin only).
    """
    cursor = db.reviews.find().sort("created_at", -1).skip(skip).limit(limit)
    return await cursor.to_list(length=limit)

@router.get("/product/{product_id}", response_model=List[ReviewResponse])
async def read_product_reviews(
    product_id: str,
    skip: int = 0,
    limit: int = 100,
    db = Depends(get_database)
):
    """
    Get all reviews for a specific product.
    """
    try:
        return await get_reviews_for_product(db, product_id, skip=skip, limit=limit)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Product ID")

@router.put("/{review_id}", response_model=ReviewResponse)
async def update_existing_review(
    review_id: str,
    review_in: ReviewUpdate,
    db = Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Update a review (Must be author).
    """
    try:
        review = await get_review(db, review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
            
        if review["user_id"] != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not enough permissions")
            
        updated_review = await update_review(db, review_id, review_in)
        return updated_review
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Review ID")

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_review(
    review_id: str,
    db = Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Delete a review (Author or Admin).
    """
    try:
        review = await get_review(db, review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
            
        if review["user_id"] != str(current_user.id) and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Not enough permissions")
            
        await delete_review(db, review_id)
        return None
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Review ID")

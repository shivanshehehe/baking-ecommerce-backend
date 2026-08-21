from datetime import datetime, timezone
from typing import List, Optional
from bson import ObjectId
from app.schemas.review import ReviewCreate, ReviewInDB, ReviewUpdate
from app.models.product import get_product, update_product
from app.schemas.product import ProductUpdate

async def recalculate_product_rating(db, product_id: str):
    cursor = db.reviews.aggregate([
        {"$match": {"product_id": product_id}},
        {"$group": {"_id": "$product_id", "average_rating": {"$avg": "$rating"}}}
    ])
    result = await cursor.to_list(length=1)
    if result:
        avg_rating = result[0]["average_rating"]
        await db.products.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": {"average_rating": avg_rating}}
        )
    else:
        await db.products.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": {"average_rating": 0.0}}
        )

async def create_review(db, user_id: str, review_in: ReviewCreate) -> dict:
    db_review = ReviewInDB(
        **review_in.model_dump(),
        user_id=user_id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    result = await db.reviews.insert_one(db_review.model_dump(by_alias=True, exclude_none=True))
    await recalculate_product_rating(db, review_in.product_id)
    return await db.reviews.find_one({"_id": result.inserted_id})

async def get_reviews_for_product(db, product_id: str, skip: int = 0, limit: int = 100) -> List[dict]:
    cursor = db.reviews.find({"product_id": product_id}).sort("created_at", -1).skip(skip).limit(limit)
    return await cursor.to_list(length=limit)

async def get_review(db, review_id: str) -> Optional[dict]:
    return await db.reviews.find_one({"_id": ObjectId(review_id)})

async def update_review(db, review_id: str, review_in: ReviewUpdate) -> Optional[dict]:
    update_data = {k: v for k, v in review_in.model_dump(exclude_unset=True).items() if v is not None}
    if not update_data:
        return await get_review(db, review_id)
        
    update_data["updated_at"] = datetime.now(timezone.utc)
    await db.reviews.update_one(
        {"_id": ObjectId(review_id)},
        {"$set": update_data}
    )
    review = await get_review(db, review_id)
    if review:
        await recalculate_product_rating(db, review["product_id"])
    return review

async def delete_review(db, review_id: str) -> bool:
    review = await get_review(db, review_id)
    if not review:
        return False
        
    result = await db.reviews.delete_one({"_id": ObjectId(review_id)})
    if result.deleted_count > 0:
        await recalculate_product_rating(db, review["product_id"])
        return True
    return False

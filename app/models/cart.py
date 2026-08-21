from datetime import datetime, timezone
from typing import List, Optional
from bson import ObjectId
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartItemInDB

async def add_to_cart(db, user_id: str, item_in: CartItemCreate) -> dict:
    # Check if item already exists in cart for this user
    existing_item = await db.cart.find_one({
        "user_id": user_id,
        "product_id": item_in.product_id
    })
    
    if existing_item:
        # Update quantity
        new_quantity = existing_item["quantity"] + item_in.quantity
        await db.cart.update_one(
            {"_id": existing_item["_id"]},
            {"$set": {"quantity": new_quantity}}
        )
        return await db.cart.find_one({"_id": existing_item["_id"]})
    
    # Add new item
    db_item = CartItemInDB(
        **item_in.model_dump(),
        user_id=user_id,
        added_at=datetime.now(timezone.utc)
    )
    result = await db.cart.insert_one(db_item.model_dump(by_alias=True, exclude_none=True))
    return await db.cart.find_one({"_id": result.inserted_id})

async def get_cart_items(db, user_id: str) -> List[dict]:
    cursor = db.cart.find({"user_id": user_id})
    return await cursor.to_list(length=100)

async def update_cart_item(db, item_id: str, user_id: str, item_in: CartItemUpdate) -> Optional[dict]:
    result = await db.cart.update_one(
        {"_id": ObjectId(item_id), "user_id": user_id},
        {"$set": {"quantity": item_in.quantity}}
    )
    if result.modified_count > 0:
        return await db.cart.find_one({"_id": ObjectId(item_id)})
    return None

async def remove_from_cart(db, item_id: str, user_id: str) -> bool:
    result = await db.cart.delete_one({"_id": ObjectId(item_id), "user_id": user_id})
    return result.deleted_count > 0

async def clear_cart(db, user_id: str):
    await db.cart.delete_many({"user_id": user_id})

from datetime import datetime, timezone
from typing import List, Optional
from bson import ObjectId
from app.schemas.order import OrderCreate, OrderInDB, OrderItemSchema, OrderStatus

async def create_order(db, user_id: str, order_in: OrderCreate, items: List[dict]) -> Optional[dict]:
    # Calculate total
    total_amount = sum(item["quantity"] * item["price"] for item in items)
    
    order_items = [
        OrderItemSchema(product_id=item["product_id"], quantity=item["quantity"], price=item["price"])
        for item in items
    ]

    db_order = OrderInDB(
        user_id=user_id,
        status=OrderStatus.pending,
        total_amount=total_amount,
        shipping_address=order_in.shipping_address,
        order_items=order_items,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    result = await db.orders.insert_one(db_order.model_dump(by_alias=True, exclude_none=True))
    return await db.orders.find_one({"_id": result.inserted_id})

async def get_user_orders(db, user_id: str) -> List[dict]:
    cursor = db.orders.find({"user_id": user_id}).sort("created_at", -1)
    return await cursor.to_list(length=100)

async def get_order(db, order_id: str) -> Optional[dict]:
    return await db.orders.find_one({"_id": ObjectId(order_id)})

async def update_order_status(db, order_id: str, status: str) -> Optional[dict]:
    result = await db.orders.update_one(
        {"_id": ObjectId(order_id)},
        {
            "$set": {
                "status": status,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    if result.modified_count > 0:
        return await get_order(db, order_id)
    return None

async def get_all_orders(db, skip: int = 0, limit: int = 100) -> List[dict]:
    cursor = db.orders.find().sort("created_at", -1).skip(skip).limit(limit)
    return await cursor.to_list(length=limit)

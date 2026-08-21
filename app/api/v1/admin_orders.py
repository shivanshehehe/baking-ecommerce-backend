from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from bson.errors import InvalidId

from app.database.connection import get_database
from app.api.deps import get_current_admin_user
from app.schemas.user import UserResponse
from app.schemas.order import OrderResponse, OrderStatusUpdate
from app.models.order import get_all_orders, get_order, update_order_status

router = APIRouter()

@router.get("/orders", response_model=List[OrderResponse])
async def read_all_orders(
    skip: int = 0,
    limit: int = 100,
    db = Depends(get_database),
    current_admin: UserResponse = Depends(get_current_admin_user)
):
    """
    Retrieve all customer orders. (Admin only)
    """
    return await get_all_orders(db, skip=skip, limit=limit)

@router.get("/orders/analytics")
async def get_order_analytics(
    db = Depends(get_database),
    current_admin: UserResponse = Depends(get_current_admin_user)
):
    """
    Get backend e-commerce metrics including total revenue, order count, and status breakdown. (Admin only)
    """
    pipeline = [
        {
            "$group": {
                "_id": "$status",
                "count": {"$sum": 1},
                "total_sales": {"$sum": "$total_amount"}
            }
        }
    ]
    cursor = db.orders.aggregate(pipeline)
    results = await cursor.to_list(length=100)
    
    total_sales = 0.0
    total_orders = 0
    status_breakdown = {}
    
    for r in results:
        status_name = r["_id"]
        count = r["count"]
        sales = r["total_sales"]
        
        status_breakdown[status_name] = count
        total_orders += count
        if status_name != "cancelled":
            total_sales += sales
            
    return {
        "total_sales": round(total_sales, 2),
        "total_orders": total_orders,
        "status_breakdown": status_breakdown
    }

@router.put("/orders/{order_id}/status", response_model=OrderResponse)
async def update_order_status_admin(
    order_id: str,
    status_update: OrderStatusUpdate,
    db = Depends(get_database),
    current_admin: UserResponse = Depends(get_current_admin_user)
):
    """
    Update the status of a specific order. (Admin only)
    """
    try:
        order = await get_order(db, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
            
        updated_order = await update_order_status(db, order_id, status_update.status)
        return updated_order
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Order ID")

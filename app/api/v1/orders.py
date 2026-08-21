from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from bson.errors import InvalidId

from app.database.connection import get_database
from app.api.deps import get_current_user
from app.schemas.user import UserResponse
from app.schemas.order import OrderCreate, OrderResponse, OrderStatus
from app.models.order import create_order, get_user_orders, get_order, update_order_status
from app.models.cart import get_cart_items, clear_cart
from app.models.product import get_product, update_product
from app.schemas.product import ProductUpdate

router = APIRouter()

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def place_order(
    order_in: OrderCreate,
    db = Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Create an order from the current cart.
    """
    cart_items = await get_cart_items(db, user_id=str(current_user.id))
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    order_items = []
    
    # Check inventory and calculate prices
    for item in cart_items:
        product = await get_product(db, item["product_id"])
        if not product or not product.get("is_active", True):
            raise HTTPException(status_code=400, detail=f"Product {item['product_id']} not available")
            
        if product.get("stock_quantity", 0) < item["quantity"]:
            raise HTTPException(status_code=400, detail=f"Not enough stock for {product['name']}")
            
        order_items.append({
            "product_id": item["product_id"],
            "quantity": item["quantity"],
            "price": product["price"]
        })

    # Create the order
    order = await create_order(db, user_id=str(current_user.id), order_in=order_in, items=order_items)
    
    # Reduce inventory
    for item in cart_items:
        product = await get_product(db, item["product_id"])
        new_stock = product["stock_quantity"] - item["quantity"]
        await update_product(db, item["product_id"], ProductUpdate(stock_quantity=new_stock))
        
    # Clear the cart
    await clear_cart(db, user_id=str(current_user.id))
    
    return order

@router.get("/", response_model=List[OrderResponse])
async def read_user_orders(
    db = Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get current user's order history.
    """
    return await get_user_orders(db, user_id=str(current_user.id))

@router.get("/{order_id}", response_model=OrderResponse)
async def read_order(
    order_id: str,
    db = Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get details of a specific order.
    """
    try:
        order = await get_order(db, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
            
        if order["user_id"] != str(current_user.id) and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Not enough permissions")
            
        return order
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Order ID")

@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: str,
    db = Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Cancel an order if status allows.
    """
    try:
        order = await get_order(db, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
            
        if order["user_id"] != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not enough permissions")
            
        if order["status"] != OrderStatus.pending:
            raise HTTPException(status_code=400, detail="Only pending orders can be cancelled")
            
        updated_order = await update_order_status(db, order_id, OrderStatus.cancelled)
        
        # Restore inventory
        for item in order["order_items"]:
            product = await get_product(db, item["product_id"])
            if product:
                new_stock = product["stock_quantity"] + item["quantity"]
                await update_product(db, item["product_id"], ProductUpdate(stock_quantity=new_stock))
                
        return updated_order
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Order ID")

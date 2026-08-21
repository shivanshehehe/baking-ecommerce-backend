from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from bson.errors import InvalidId

from app.database.connection import get_database
from app.api.deps import get_current_user
from app.schemas.user import UserResponse
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartItemResponse
from app.models.cart import add_to_cart, get_cart_items, update_cart_item, remove_from_cart
from app.models.product import get_product

router = APIRouter()

@router.post("/add", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
async def add_item_to_cart(
    item_in: CartItemCreate,
    db = Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Add a product to the shopping cart.
    """
    try:
        # Check if product exists and has stock
        product = await get_product(db, item_in.product_id)
        if not product or not product.get("is_active", True):
            raise HTTPException(status_code=404, detail="Product not found")
            
        if product.get("stock_quantity", 0) < item_in.quantity:
            raise HTTPException(status_code=400, detail="Not enough stock available")
            
        cart_item = await add_to_cart(db, user_id=str(current_user.id), item_in=item_in)
        return cart_item
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Product ID")

@router.get("/", response_model=List[CartItemResponse])
async def view_cart(
    db = Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    View current user's shopping cart.
    """
    return await get_cart_items(db, user_id=str(current_user.id))

@router.put("/update/{item_id}", response_model=CartItemResponse)
async def update_cart_item_quantity(
    item_id: str,
    item_in: CartItemUpdate,
    db = Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Update quantity of an item in the cart.
    """
    try:
        updated_item = await update_cart_item(db, item_id=item_id, user_id=str(current_user.id), item_in=item_in)
        if not updated_item:
            raise HTTPException(status_code=404, detail="Cart item not found")
        return updated_item
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Item ID")

@router.delete("/remove/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item_from_cart(
    item_id: str,
    db = Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Remove an item from the cart.
    """
    try:
        success = await remove_from_cart(db, item_id=item_id, user_id=str(current_user.id))
        if not success:
            raise HTTPException(status_code=404, detail="Cart item not found")
        return None
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Item ID")

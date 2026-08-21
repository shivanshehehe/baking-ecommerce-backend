from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from bson.errors import InvalidId

from app.database.connection import get_database
from app.schemas.product import ProductResponse, CategoryResponse
from app.models.product import get_product, get_categories

router = APIRouter()

@router.get("/", response_model=List[ProductResponse])
async def read_public_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category_id: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db = Depends(get_database)
):
    """
    Retrieve products for customers with filtering and pagination.
    """
    query = {"is_active": True}
    
    if category_id:
        query["category_id"] = category_id
        
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
        
    if min_price is not None or max_price is not None:
        price_query = {}
        if min_price is not None:
            price_query["$gte"] = min_price
        if max_price is not None:
            price_query["$lte"] = max_price
        query["price"] = price_query

    cursor = db.products.find(query).skip(skip).limit(limit)
    products = await cursor.to_list(length=limit)
    return products

@router.get("/categories", response_model=List[CategoryResponse])
async def read_public_categories(
    db = Depends(get_database)
):
    """
    Retrieve all product categories for customers.
    """
    return await get_categories(db)

@router.get("/{product_id}", response_model=ProductResponse)
async def read_public_product(
    product_id: str,
    db = Depends(get_database)
):
    """
    Retrieve product details for customers.
    """
    try:
        product = await get_product(db, product_id)
        if not product or not product.get("is_active", True):
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Product ID")

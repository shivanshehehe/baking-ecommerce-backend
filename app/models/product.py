from datetime import datetime, timezone
from typing import List, Optional
from bson import ObjectId
from app.schemas.product import ProductCreate, ProductUpdate, ProductInDB, CategoryCreate

# Category operations
async def create_category(db, category_in: CategoryCreate) -> dict:
    result = await db.categories.insert_one(category_in.model_dump())
    return await db.categories.find_one({"_id": result.inserted_id})

async def get_categories(db) -> List[dict]:
    cursor = db.categories.find()
    return await cursor.to_list(length=100)

async def get_category(db, category_id: str) -> Optional[dict]:
    return await db.categories.find_one({"_id": ObjectId(category_id)})

# Product operations
async def create_product(db, product_in: ProductCreate, admin_id: str) -> dict:
    db_product = ProductInDB(
        **product_in.model_dump(),
        created_by=admin_id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    result = await db.products.insert_one(
        db_product.model_dump(by_alias=True, exclude_none=True)
    )
    return await db.products.find_one({"_id": result.inserted_id})

async def get_product(db, product_id: str) -> Optional[dict]:
    return await db.products.find_one({"_id": ObjectId(product_id)})

async def get_products(db, skip: int = 0, limit: int = 100) -> List[dict]:
    cursor = db.products.find().skip(skip).limit(limit)
    return await cursor.to_list(length=limit)

async def update_product(db, product_id: str, product_in: ProductUpdate) -> Optional[dict]:
    update_data = {k: v for k, v in product_in.model_dump(exclude_unset=True).items() if v is not None}
    if not update_data:
        return await get_product(db, product_id)
        
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    await db.products.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": update_data}
    )
    return await get_product(db, product_id)

async def delete_product(db, product_id: str) -> bool:
    result = await db.products.delete_one({"_id": ObjectId(product_id)})
    return result.deleted_count > 0

from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from app.schemas.user import PyObjectId
from bson import ObjectId


# --- Category Schemas ---

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: PyObjectId = Field(validation_alias="_id")

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }


# --- Product Schemas ---

class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    description: str
    price: float = Field(..., gt=0, description="Price must be greater than 0")
    sku: str = Field(..., min_length=2, max_length=50, description="Stock Keeping Unit - unique identifier")
    category_id: str
    stock_quantity: int = Field(0, ge=0)
    images: List[str] = []
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    sku: Optional[str] = None
    category_id: Optional[str] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    images: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ProductInDB(ProductBase):
    id: Optional[PyObjectId] = Field(validation_alias="_id", default=None)
    created_by: str  # admin user_id as string
    average_rating: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"populate_by_name": True, "arbitrary_types_allowed": True}


class ProductResponse(ProductBase):
    id: PyObjectId = Field(validation_alias="_id")
    created_by: str
    average_rating: float = 0.0
    created_at: datetime
    updated_at: datetime

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

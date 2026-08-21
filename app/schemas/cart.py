from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.user import PyObjectId
from bson import ObjectId


class CartItemBase(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0, description="Quantity must be at least 1")


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0, description="Quantity must be at least 1")


class CartItemInDB(CartItemBase):
    id: Optional[PyObjectId] = Field(validation_alias="_id", default=None)
    user_id: str
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"populate_by_name": True, "arbitrary_types_allowed": True}


class CartItemResponse(CartItemBase):
    id: PyObjectId = Field(validation_alias="_id")
    user_id: str
    added_at: datetime

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

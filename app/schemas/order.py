from datetime import datetime, timezone
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from app.schemas.user import PyObjectId

class OrderStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"

class Address(BaseModel):
    street: str
    city: str
    state: str
    postal_code: str
    country: str

class OrderItemSchema(BaseModel):
    product_id: str
    quantity: int
    price: float

class OrderCreate(BaseModel):
    shipping_address: Address

class OrderStatusUpdate(BaseModel):
    status: OrderStatus

class OrderInDB(BaseModel):
    id: Optional[PyObjectId] = Field(validation_alias="_id", default=None)
    user_id: str
    status: OrderStatus = OrderStatus.pending
    total_amount: float
    shipping_address: Address
    order_items: List[OrderItemSchema]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }


class OrderResponse(OrderInDB):
    id: PyObjectId = Field(validation_alias="_id")

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

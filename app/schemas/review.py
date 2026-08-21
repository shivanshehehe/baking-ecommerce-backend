from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.user import PyObjectId

class ReviewBase(BaseModel):
    product_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None

class ReviewInDB(ReviewBase):
    id: Optional[PyObjectId] = Field(validation_alias="_id", default=None)
    user_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }


class ReviewResponse(ReviewInDB):
    id: PyObjectId = Field(validation_alias="_id")
    user_id: str
    created_at: datetime

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

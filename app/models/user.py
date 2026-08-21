from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from app.schemas.user import UserCreate, UserInDB
from app.core.security import get_password_hash

async def get_user_by_email(db, email: str) -> Optional[dict]:
    return await db.users.find_one({"email": email})

async def get_user_by_username(db, username: str) -> Optional[dict]:
    return await db.users.find_one({"username": username})

async def create_user(db, user_in: UserCreate) -> dict:
    hashed_password = get_password_hash(user_in.password)
    db_user = UserInDB(
        **user_in.model_dump(exclude={"password"}),
        hashed_password=hashed_password,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    result = await db.users.insert_one(
        db_user.model_dump(by_alias=True, exclude_none=True)
    )
    return await db.users.find_one({"_id": result.inserted_id})

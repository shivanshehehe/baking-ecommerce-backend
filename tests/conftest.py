import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database.connection import db, connect_to_mongo, close_mongo_connection
from app.core.config import settings

@pytest.fixture
async def async_client():
    # Configure settings for test database
    settings.DATABASE_NAME = "test_baking_ecommerce"
    await connect_to_mongo()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
        
    # Teardown: drop test database and close connection
    if db.client:
        await db.client.drop_database("test_baking_ecommerce")
    await close_mongo_connection()

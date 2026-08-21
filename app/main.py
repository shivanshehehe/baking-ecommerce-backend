import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.database.connection import connect_to_mongo, close_mongo_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    # Ensure uploads directory exists
    os.makedirs("uploads", exist_ok=True)
    # Startup: connect to MongoDB
    await connect_to_mongo()
    yield
    # Shutdown: close MongoDB connection
    await close_mongo_connection()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API for a Baking E-Commerce platform (similar to Theobroma). "
                "Supports customers and admin users with full product, cart, order, and review management.",
    lifespan=lifespan,
    contact={"name": "Baking E-commerce Team"},
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production (e.g. specific frontend URL)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include API Router ---
from app.api.v1.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)

# --- Mount Static Files (for product images) ---
app.mount("/static", StaticFiles(directory="uploads"), name="static")


# --- Root Endpoints ---
@app.get("/", tags=["Root"])
async def root():
    """Welcome message and docs URL."""
    return {
        "message": "Welcome to the Baking E-commerce API 🎂",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }


@app.get("/health", tags=["Root"])
async def health_check():
    """Health check endpoint. Verifies API is running and DB is connected."""
    from app.database.connection import db
    db_status = "connected" if db.client else "disconnected"
    return {
        "status": "healthy",
        "database": db_status,
    }

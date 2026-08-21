from fastapi import APIRouter
from app.api.v1 import auth, admin_products, images, products, cart, orders, reviews, admin_orders

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(admin_products.router, prefix="/admin", tags=["admin-products"])
api_router.include_router(images.router, prefix="/admin", tags=["admin-images"])
api_router.include_router(admin_orders.router, prefix="/admin", tags=["admin-orders"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(cart.router, prefix="/cart", tags=["cart"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])

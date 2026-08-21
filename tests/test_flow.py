import pytest
from app.database.connection import db

@pytest.mark.asyncio
async def test_full_ecommerce_flow(async_client):
    # -------------------------------------------------------------
    # 1. User Registration & Setup
    # -------------------------------------------------------------
    # Register customer
    cust_resp = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "customer@example.com", "username": "customer", "password": "password123"}
    )
    assert cust_resp.status_code == 201
    customer_data = cust_resp.json()
    customer_id = customer_data["id"]
    
    # Register admin
    admin_resp = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "admin@example.com", "username": "adminuser", "password": "password123"}
    )
    assert admin_resp.status_code == 201
    admin_data = admin_resp.json()
    admin_id = admin_data["id"]
    
    # Promote admin user in the database
    from bson import ObjectId
    await db.db.users.update_one({"_id": ObjectId(admin_id)}, {"$set": {"is_admin": True}})
    
    # -------------------------------------------------------------
    # 2. Login & Get Tokens
    # -------------------------------------------------------------
    # Customer login
    cust_login_resp = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "customer", "password": "password123"}
    )
    assert cust_login_resp.status_code == 200
    cust_token = cust_login_resp.json()["access_token"]
    cust_headers = {"Authorization": f"Bearer {cust_token}"}
    
    # Admin login
    admin_login_resp = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "adminuser", "password": "password123"}
    )
    assert admin_login_resp.status_code == 200
    admin_token = admin_login_resp.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # -------------------------------------------------------------
    # 3. Category Operations (Admin-only)
    # -------------------------------------------------------------
    # Admin creates category
    cat_resp = await async_client.post(
        "/api/v1/admin/categories",
        json={"name": "Cakes", "description": "Delicious baked cakes"},
        headers=admin_headers
    )
    assert cat_resp.status_code == 201
    category = cat_resp.json()
    category_id = category["id"]
    
    # Admin gets category by ID
    get_cat_resp = await async_client.get(
        f"/api/v1/admin/categories/{category_id}",
        headers=admin_headers
    )
    assert get_cat_resp.status_code == 200
    assert get_cat_resp.json()["name"] == "Cakes"

    # -------------------------------------------------------------
    # 4. Product Operations (Admin-only)
    # -------------------------------------------------------------
    # Admin creates product
    prod_resp = await async_client.post(
        "/api/v1/admin/products",
        json={
            "name": "Chocolate Cake",
            "description": "Rich Belgian chocolate cake",
            "price": 25.0,
            "sku": "CHOC-CAKE-01",
            "category_id": category_id,
            "stock_quantity": 10,
            "is_active": True
        },
        headers=admin_headers
    )
    assert prod_resp.status_code == 201
    product = prod_resp.json()
    product_id = product["id"]

    # -------------------------------------------------------------
    # 5. Public Product Browsing (Customers)
    # -------------------------------------------------------------
    # Public list products
    pub_prod_list = await async_client.get("/api/v1/products/")
    assert pub_prod_list.status_code == 200
    assert len(pub_prod_list.json()) == 1
    assert pub_prod_list.json()[0]["name"] == "Chocolate Cake"
    
    # Public categories list
    pub_cat_list = await async_client.get("/api/v1/products/categories")
    assert pub_cat_list.status_code == 200
    assert len(pub_cat_list.json()) == 1
    assert pub_cat_list.json()[0]["name"] == "Cakes"
    
    # Public search cake
    search_resp = await async_client.get("/api/v1/products/?search=chocolate")
    assert search_resp.status_code == 200
    assert len(search_resp.json()) == 1

    # -------------------------------------------------------------
    # 6. Shopping Cart Operations (Customers)
    # -------------------------------------------------------------
    # Add to cart
    add_cart = await async_client.post(
        "/api/v1/cart/add",
        json={"product_id": product_id, "quantity": 2},
        headers=cust_headers
    )
    assert add_cart.status_code == 201
    
    # View cart
    view_cart = await async_client.get("/api/v1/cart/", headers=cust_headers)
    assert view_cart.status_code == 200
    cart_items = view_cart.json()
    assert len(cart_items) == 1
    assert cart_items[0]["quantity"] == 2

    # -------------------------------------------------------------
    # 7. Order Operations (Customers & Admins)
    # -------------------------------------------------------------
    # Place order
    checkout_resp = await async_client.post(
        "/api/v1/orders/",
        json={
            "shipping_address": {
                "street": "123 Baker St",
                "city": "London",
                "state": "Greater London",
                "postal_code": "NW1 6XE",
                "country": "UK"
            }
        },
        headers=cust_headers
    )
    assert checkout_resp.status_code == 201
    order = checkout_resp.json()
    order_id = order["id"]
    assert order["status"] == "pending"
    assert order["total_amount"] == 50.0 # 2 * 25.0
    
    # Check inventory reduced (10 - 2 = 8)
    get_prod = await async_client.get(f"/api/v1/products/{product_id}")
    assert get_prod.status_code == 200
    assert get_prod.json()["stock_quantity"] == 8

    # View orders history
    order_history = await async_client.get("/api/v1/orders/", headers=cust_headers)
    assert order_history.status_code == 200
    assert len(order_history.json()) == 1

    # Admin lists all orders
    admin_orders_resp = await async_client.get("/api/v1/admin/orders", headers=admin_headers)
    assert admin_orders_resp.status_code == 200
    assert len(admin_orders_resp.json()) == 1

    # Admin checks order analytics
    analytics_resp = await async_client.get("/api/v1/admin/orders/analytics", headers=admin_headers)
    assert analytics_resp.status_code == 200
    analytics = analytics_resp.json()
    assert analytics["total_sales"] == 50.0
    assert analytics["total_orders"] == 1
    assert analytics["status_breakdown"]["pending"] == 1

    # -------------------------------------------------------------
    # 8. Review & Rating Operations
    # -------------------------------------------------------------
    # Customer adds review
    review_resp = await async_client.post(
        "/api/v1/reviews/",
        json={"product_id": product_id, "rating": 5, "comment": "Amazing cake!"},
        headers=cust_headers
    )
    assert review_resp.status_code == 201
    review = review_resp.json()
    assert review["rating"] == 5
    
    # Check average rating updated
    get_prod_rated = await async_client.get(f"/api/v1/products/{product_id}")
    assert get_prod_rated.json()["average_rating"] == 5.0
    
    # Get reviews for product
    prod_reviews = await async_client.get(f"/api/v1/reviews/product/{product_id}")
    assert prod_reviews.status_code == 200
    assert len(prod_reviews.json()) == 1
    
    # Admin gets all reviews
    all_reviews_resp = await async_client.get("/api/v1/reviews/admin/all", headers=admin_headers)
    assert all_reviews_resp.status_code == 200
    assert len(all_reviews_resp.json()) == 1

    # -------------------------------------------------------------
    # 9. Admin Updates Order Status
    # -------------------------------------------------------------
    status_update_resp = await async_client.put(
        f"/api/v1/admin/orders/{order_id}/status",
        json={"status": "confirmed"},
        headers=admin_headers
    )
    assert status_update_resp.status_code == 200
    assert status_update_resp.json()["status"] == "confirmed"

    # -------------------------------------------------------------
    # 10. Admin Delete Category Constraints
    # -------------------------------------------------------------
    # Deleting category containing products should fail with 400
    del_cat_fail = await async_client.delete(
        f"/api/v1/admin/categories/{category_id}",
        headers=admin_headers
    )
    assert del_cat_fail.status_code == 400

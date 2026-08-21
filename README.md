# 🍰 Baking E-Commerce Backend (FastAPI + MongoDB) 

A complete, premium backend API system for a baking e-commerce platform (similar to Theobroma), built with **FastAPI** and **MongoDB (Motor)**. 

This project covers all requirements from **Week 1 to Week 9**, offering features like role-based authentication, shopping carts, inventory checking, order checkouts, rating/reviews systems, secure local image uploading, business analytics, and a pytest integration suite.

---

## 🌟 Key Features (Weeks 1-9)

- **Week 1 (Foundation):** Clean application layout, MongoDB connections, health-checks, CORS, configuration settings.
- **Week 2 (Authentication):** Secure signup and login using **JWT Tokens** and **bcrypt** password hashing. User role management.
- **Week 3 (Admin Products & Categories):** Complete admin-only CRUD for product items and categories.
- **Week 4 (Image Uploading):** Endpoint to upload product images locally with type and size validations, plus static files mounting.
- **Week 5 (Public Browsing & Cart):** Searching, pagination, and range filtering for products. Session shopping cart management.
- **Week 6 (Orders):** Cart checkout, inventory checks/deductions, status logging, and user cancellation.
- **Week 7 (Reviews & Ratings):** Double-entry purchase verification (users can only review what they bought) and dynamic product average rating recalculation.
- **Week 8 (Testing & Docker):** Pytest suite for end-to-end user flows, `Dockerfile` and `docker-compose.yml` setups.
- **Week 9 (Admin Refinements):** Advanced order analytics (revenue, order counts, status breakdowns), category deletions safety check (blocks deletion if active products exist), and admin image cleanup.

---

## 🗂️ Project Directory Layout

```text
├── app/
│   ├── api/
│   │   ├── deps.py               # Authentication and role dependencies
│   │   └── v1/
│   │       ├── api.py            # Main API v1 Router inclusion
│   │       ├── auth.py           # Register, login, and user profile
│   │       ├── products.py       # Public product search/catalog
│   │       ├── cart.py           # Customer shopping cart
│   │       ├── orders.py         # Customer order history and checkout
│   │       ├── reviews.py        # Customer product reviews
│   │       ├── admin_products.py # Admin category/product CRUD
│   │       ├── admin_orders.py   # Admin order listings and sales analytics
│   │       └── images.py         # Admin product image upload/deletion
│   ├── core/
│   │   ├── config.py             # App environment variables & settings
│   │   └── security.py           # Token creation and bcrypt password hashing
│   ├── database/
│   │   └── connection.py         # MongoDB client initialization (Motor)
│   ├── models/                   # DB queries and business logic operations
│   ├── schemas/                  # Pydantic v2 schemas
│   └── main.py                   # FastAPI app entry point, static files mounting
├── tests/                        # Automated pytest suite
│   ├── conftest.py               # Shared test fixtures (async_client)
│   ├── test_auth.py              # User authentication tests
│   └── test_flow.py              # Full integration e-commerce flow tests
├── uploads/                      # Local filesystem storage for product images
├── requirements.txt              # Production and test dependencies
└── Dockerfile                    # Containerization setup
```

---

## 🚀 Local Development Setup

### 1. Clone & Navigate
```bash
git clone <repository_url>
cd baking-ecommerce-backend
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Packages
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Copy `.env.example` to `.env` and adjust the variables if needed:
```bash
cp .env.example .env
```
Default configuration values:
- `MONGODB_URL`: `mongodb://localhost:27017`
- `DATABASE_NAME`: `baking_ecommerce`
- `SECRET_KEY`: Random secret string used for JWT encoding.

### 5. Run Server
Start the development server with hot-reloading:
```bash
uvicorn app.main:app --reload
```
Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser to view the interactive Swagger API documentation.

---

## 🧪 Running Tests

A complete integration suite is included. Make sure MongoDB is running locally, then execute:
```bash
pytest
```
This runs:
- `tests/test_auth.py`: Simple user registration and JWT login verification.
- `tests/test_flow.py`: Full integration flow test (Admin Category & Product Creation -> Customer Public Catalog Search -> Cart Additions -> Order Checkout -> Inventory Reduction -> Admin Analytics & Review Moderation).

---

## 📌 API Endpoints Reference

### 🔐 Authentication (`/api/v1/auth`)
* `POST /register`: Registers a new customer account.
* `POST /login`: Logs in using username and password, returns JWT token.
* `GET /me`: Returns the logged-in user's profile.

### 🎂 Public Product Catalog (`/api/v1/products`)
* `GET /`: Lists all active products. Supports query parameters `skip`, `limit`, `category_id`, `search` (name & description), `min_price`, and `max_price`.
* `GET /categories`: Lists all public categories.
* `GET /{product_id}`: Retrieves detailed information for a single product.

### 🛒 Shopping Cart (`/api/v1/cart`)
* `POST /add`: Adds a specific quantity of a product to the cart (checks inventory).
* `GET /`: Lists all items currently in the customer's cart.
* `PUT /update/{item_id}`: Updates cart quantity.
* `DELETE /remove/{item_id}`: Removes an item from the cart.

### 📦 Customer Orders (`/api/v1/orders`)
* `POST /`: Checks out the current cart, reduces stock levels, and creates a pending order.
* `GET /`: Lists the logged-in customer's order history.
* `GET /{order_id}`: Gets the details of a specific order.
* `POST /{order_id}/cancel`: Cancels a pending order and restores product inventory back to stock.

### ⭐ Reviews & Ratings (`/api/v1/reviews`)
* `POST /`: Adds a star rating (1-5) and comment (requires customer to have purchased the item).
* `GET /product/{product_id}`: Gets all public reviews for a product.
* `GET /admin/all`: Lists all reviews for admin moderation.
* `PUT /{review_id}`: Updates a review (author only).
* `DELETE /{review_id}`: Deletes a review (author or admin).

### 🛠️ Admin Management (`/api/v1/admin`)

#### Categories & Products
* `POST /categories`: Creates a new product category.
* `GET /categories`: Lists all categories (admin view).
* `GET /categories/{category_id}`: Gets a single category.
* `DELETE /categories/{category_id}`: Deletes a category (fails if any product is under it).
* `POST /products`: Creates a new product.
* `GET /products`: Lists all products (active or inactive).
* `PUT /products/{product_id}`: Updates a product details.
* `DELETE /products/{product_id}`: Deletes a product.

#### Image Management
* `POST /products/{product_id}/images`: Uploads a JPEG/PNG/WEBP product image under 5MB to `/uploads`.
* `DELETE /products/{product_id}/images/{filename}`: Deletes an image from local disk and product images array.

#### Orders & Business Analytics
* `GET /orders`: View all customer orders.
* `PUT /orders/{order_id}/status`: Update order status (`pending`, `confirmed`, `shipped`, `delivered`, `cancelled`).
* `GET /orders/analytics`: Aggregates business data: total sales revenue, volume of orders, and order counts grouped by status.

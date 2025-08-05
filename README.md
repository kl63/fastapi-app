# FreshCart E-Commerce API

A comprehensive e-commerce backend API built with FastAPI, PostgreSQL, and modern Python practices. This API provides all the essential features needed for a full-featured online grocery/e-commerce platform.

## 🚀 Features

### Core E-Commerce Features
- **User Management**: Registration, authentication, profile management
- **Product Catalog**: Categories, products with detailed information, search & filtering
- **Shopping Cart**: Add/remove items, quantity management, discount codes
- **Wishlist**: Save favorite products for later
- **Order Management**: Complete order processing workflow
- **Address Management**: Multiple shipping/billing addresses
- **Reviews & Ratings**: Product reviews and rating system
- **Notifications**: In-app notification system
- **Coupon System**: Discount codes and promotions

### Technical Features
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access**: Admin and user permissions
- **Database Migrations**: Alembic for schema management
- **API Documentation**: Auto-generated Swagger/OpenAPI docs
- **Data Validation**: Pydantic schemas for request/response validation
- **CORS Support**: Cross-origin resource sharing
- **Error Handling**: Comprehensive error responses

## 🛠️ Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Robust relational database
- **SQLAlchemy**: Python SQL toolkit and ORM
- **Alembic**: Database migration tool
- **Pydantic**: Data validation using Python type annotations
- **JWT**: JSON Web Tokens for authentication
- **Uvicorn**: ASGI server implementation
- **Bcrypt**: Password hashing

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip or poetry for package management

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd fastapi-app
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
cp .env.example .env
# Edit .env with your database credentials
```

Required environment variables:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/fastapi_app
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=["http://localhost:3000"]
```

### 3. Database Setup

```bash
# Run deployment script (creates DB and runs migrations)
python scripts/deploy.py

# Or manually:
# createdb fastapi_app
# alembic upgrade head
```

### 4. Start the Server

```bash
# Development
uvicorn main:app --reload

# Or use the startup script
./scripts/start.sh
```

### 5. Access the API

- **API Base URL**: http://localhost:8000/api/v1
- **Swagger Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📚 API Endpoints

### 🔐 Authentication (`/auth`)
- `POST /register` - Register new user
- `POST /login` - User login (OAuth2 compatible)
- `POST /logout` - User logout
- `POST /forgot-password` - Request password reset
- `POST /reset-password` - Reset password with token

### 👤 Users (`/users`)
- `GET /profile` - Get current user profile
- `PUT /profile` - Update user profile
- `PUT /password` - Change password
- `GET /me` - Get current user (legacy endpoint)

### 🏠 Addresses (`/addresses`)
- `GET /` - Get user addresses
- `POST /` - Create new address
- `GET /{id}` - Get specific address
- `PUT /{id}` - Update address
- `DELETE /{id}` - Delete address
- `PUT /{id}/default` - Set as default address

### 📂 Categories (`/categories`)
- `GET /` - List categories (with hierarchy support)
- `POST /` - Create category (admin only)
- `GET /{id}` - Get category details
- `PUT /{id}` - Update category (admin only)
- `DELETE /{id}` - Delete category (admin only)

### 🛍️ Products (`/products`)
- `GET /` - List products (with filtering & pagination)
- `POST /` - Create product (admin only)
- `GET /featured` - Get featured products
- `GET /search` - Search products
- `GET /{id}` - Get product details
- `PUT /{id}` - Update product (admin only)
- `PUT /{id}/stock` - Update stock (admin only)
- `DELETE /{id}` - Delete product (admin only)
- `GET /{id}/related` - Get related products

### 🛒 Shopping Cart (`/cart`)
- `GET /` - Get user's cart
- `POST /items` - Add item to cart
- `PUT /items/{id}` - Update cart item quantity
- `DELETE /items/{id}` - Remove item from cart
- `DELETE /` - Clear entire cart
- `POST /discount` - Apply discount code
- `DELETE /discount` - Remove discount code

### ❤️ Wishlist (`/wishlist`)
- `GET /` - Get user's wishlist
- `POST /items` - Add item to wishlist
- `DELETE /items/{product_id}` - Remove item from wishlist
- `DELETE /` - Clear entire wishlist

### 📦 Orders (`/orders`)
- `GET /` - Get user's orders
- `POST /` - Create new order
- `GET /{id}` - Get order details
- `PUT /{id}/cancel` - Cancel order
- `GET /admin/all` - Get all orders (admin only)
- `PUT /{id}/status` - Update order status (admin only)

### ⭐ Reviews (`/reviews`)
- `GET /product/{id}` - Get product reviews
- `GET /user` - Get user's reviews
- `POST /` - Create review
- `PUT /{id}` - Update review
- `DELETE /{id}` - Delete review

### 🔔 Notifications (`/notifications`)
- `GET /` - Get user notifications
- `GET /{id}` - Get specific notification
- `PUT /{id}/read` - Mark as read
- `PUT /read-all` - Mark all as read
- `DELETE /{id}` - Delete notification
- `POST /send` - Send notification (admin only)

### 🎫 Coupons (`/coupons`)
- `POST /validate` - Validate coupon code
- `GET /` - List coupons (admin only)
- `POST /` - Create coupon (admin only)
- `GET /{id}` - Get coupon (admin only)
- `PUT /{id}` - Update coupon (admin only)
- `DELETE /{id}` - Delete coupon (admin only)

## 🗄️ Database Schema

The application uses a comprehensive database schema with the following main entities:

- **Users**: User accounts with profiles and authentication
- **Addresses**: User shipping and billing addresses
- **Categories**: Product categories with hierarchy support
- **Products**: Product catalog with detailed information
- **CartItems**: Shopping cart functionality
- **WishlistItems**: User wishlists
- **Orders**: Order management with items and status history
- **Reviews**: Product reviews and ratings
- **Notifications**: User notification system
- **Coupons**: Discount codes and promotions
- **PaymentMethods**: User payment information
- **Payments**: Payment processing records

## 🧪 Testing

Run the comprehensive API test suite:

```bash
python test_api.py
```

This will test all major endpoints and provide a status report.

## 🏗️ Project Structure

```
fastapi-app/
├── app/
│   ├── api/
│   │   ├── endpoints/     # API route handlers
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── products.py
│   │   │   ├── cart.py
│   │   │   └── ...
│   │   ├── deps.py        # Dependencies
│   │   └── api.py         # Main API router
│   ├── core/
│   │   ├── config.py      # Configuration
│   │   └── security.py    # Security utilities
│   ├── crud/              # Database operations
│   │   ├── user.py
│   │   ├── product.py
│   │   └── ...
│   ├── db/
│   │   ├── base.py        # Database base
│   │   └── session.py     # Database session
│   ├── models/            # SQLAlchemy models
│   │   ├── user.py
│   │   ├── product.py
│   │   └── ...
│   └── schemas/           # Pydantic schemas
│       ├── user.py
│       ├── product.py
│       └── ...
├── alembic/               # Database migrations
├── scripts/
│   ├── deploy.py         # Deployment script
│   └── start.sh          # Startup script
├── main.py               # FastAPI application
├── test_api.py          # API test suite
└── requirements.txt      # Dependencies
```

## 🚀 Deployment

### Automated Deployment

The project includes GitHub Actions workflow for automated deployment:

```bash
# Triggers on push to main branch
# Automatically runs migrations and restarts the application
```

### Manual Deployment

```bash
# Run deployment script
python scripts/deploy.py

# Start application with PM2 or systemd
./scripts/start.sh
```

## 🔧 Development

### Adding New Features

1. **Create Model**: Add SQLAlchemy model in `app/models/`
2. **Create Schema**: Add Pydantic schemas in `app/schemas/`
3. **Create CRUD**: Add database operations in `app/crud/`
4. **Create Endpoints**: Add API routes in `app/api/endpoints/`
5. **Update Router**: Include new router in `app/api/api.py`
6. **Generate Migration**: `alembic revision --autogenerate -m "Description"`
7. **Apply Migration**: `alembic upgrade head`

### Code Quality

- Follow PEP 8 style guidelines
- Use type hints throughout the codebase
- Write comprehensive docstrings
- Add proper error handling
- Include input validation

## 📖 API Documentation

The API is fully documented with OpenAPI/Swagger:

- **Interactive Documentation**: http://localhost:8000/docs
- **Alternative Documentation**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

1. Check the [API Documentation](http://localhost:8000/docs)
2. Review the test suite in `test_api.py`
3. Check existing issues in the repository
4. Create a new issue if needed

---

**Built with ❤️ using FastAPI and modern Python practices**

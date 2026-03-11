# FreshCart E-Commerce API 🛒

A production-ready, full-featured e-commerce backend API built with FastAPI, PostgreSQL, Stripe, and modern Python practices. Designed for online grocery stores and e-commerce platforms, this API provides everything from product management to secure payment processing.

## 🌟 Overview

FreshCart API is a comprehensive backend solution that powers modern e-commerce applications. Built with performance, security, and scalability in mind, it handles everything from user authentication to payment processing, making it perfect for startups and established businesses alike.

**Live Production API**: [https://fastapi.kevinlinportfolio.com](https://fastapi.kevinlinportfolio.com)

## ✨ Key Highlights

- ✅ **80+ RESTful API endpoints** across 10 feature groups
- ✅ **Stripe payment integration** with webhooks and refunds
- ✅ **13+ database tables** with comprehensive relationships
- ✅ **JWT authentication** with role-based access control
- ✅ **Automated deployment** with GitHub Actions
- ✅ **Docker containerization** for easy deployment
- ✅ **Production-ready** with comprehensive error handling
- ✅ **Bulk data seeding** with realistic test data

## 🚀 Features

### Core E-Commerce Features
- 🛍️ **Product Catalog**: Categories with hierarchy, products with detailed specs, images, and variants
- 🛒 **Shopping Cart**: Real-time cart management, quantity updates, discount codes
- 💳 **Payment Processing**: Stripe integration with payment intents, webhooks, and refunds
- 📦 **Order Management**: Complete order lifecycle with status tracking and history
- ⭐ **Reviews & Ratings**: Product reviews with aggregated ratings
- ❤️ **Wishlist**: Save favorite products for later purchase
- 🏠 **Address Management**: Multiple shipping/billing addresses with defaults
- 🎫 **Coupon System**: Flexible discount codes with validation
- 🔔 **Notifications**: In-app notification system for order updates

### User Management
- 👤 **Authentication**: Secure registration and login with JWT tokens
- 🔐 **Authorization**: Role-based access control (Admin/User)
- 📧 **Password Recovery**: Forgot password with email tokens
- 👥 **User Profiles**: Complete profile management with preferences
- 🔒 **Security**: Bcrypt password hashing, secure token management

### Technical Features
- 🚀 **FastAPI Framework**: Async support, automatic OpenAPI docs
- 🐘 **PostgreSQL Database**: Robust relational data storage
- 🔄 **Database Migrations**: Alembic for version-controlled schema changes
- 📝 **Data Validation**: Pydantic schemas for type safety
- 🌐 **CORS Support**: Configurable cross-origin resource sharing
- 📊 **Error Handling**: Comprehensive HTTP error responses
- 🐳 **Docker Ready**: Containerized for easy deployment
- 🔧 **Automated Testing**: Test suite for API validation

## 🛠️ Tech Stack

### Backend Framework
- **FastAPI 0.104+**: Modern, fast web framework with async support
- **Python 3.8+**: Leveraging modern Python features and type hints
- **Uvicorn**: Lightning-fast ASGI server

### Database
- **PostgreSQL 12+**: Robust relational database
- **SQLAlchemy 2.0+**: Python SQL toolkit and ORM
- **Alembic**: Database migration and version control

### Payment Processing
- **Stripe API**: Secure payment processing with webhooks
- **Payment Intents**: PCI-compliant payment handling

### Security & Authentication
- **JWT (PyJWT)**: JSON Web Tokens for stateless authentication
- **Bcrypt**: Secure password hashing
- **OAuth2**: Industry-standard authorization framework

### Data Validation & Serialization
- **Pydantic v2**: Data validation using Python type annotations
- **Type Hints**: Comprehensive typing throughout the codebase

### DevOps & Deployment
- **Docker & Docker Compose**: Containerization
- **GitHub Actions**: CI/CD automation
- **Nginx**: Reverse proxy (production)
- **PM2/Systemd**: Process management (production)

## 📋 Prerequisites

### Development
- **Python 3.8+** (3.11+ recommended)
- **PostgreSQL 12+** (14+ recommended)
- **pip** or **poetry** for package management
- **Git** for version control

### Optional
- **Docker & Docker Compose** (for containerized development)
- **Stripe Account** (for payment processing features)
- **Node.js** (if integrating with frontend applications)

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
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/fastapi_app

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# Stripe Payment (Optional)
STRIPE_SECRET_KEY=sk_test_your_test_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_test_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=FreshCart API
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

### 💳 Payments (`/orders`)
- `POST /create-payment-intent` - Create Stripe payment intent
- `POST /create-order-with-payment` - Create order with payment
- `POST /confirm-payment/{id}` - Confirm payment for order
- `POST /refund/{id}` - Process refund (admin only)
- `POST /webhooks/stripe` - Stripe webhook handler

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

### Run Test Suite

All test files are organized in the `/tests` directory:

```bash
# Run all tests with pytest
pytest tests/

# Run specific test file
python tests/test_api.py

# Test authentication
python tests/test_auth_fix.py

# Test order flow
python tests/test_complete_order_flow.py

# Test Stripe payments
python tests/test_stripe_payment.py

# Check database connection
python tests/db_test.py
```

### Validation Scripts

```bash
# Check products in database
python tests/check_products.py

# Verify production cart
python tests/check_production_cart.py

# Check orders
python tests/check_orders.py
```

## 🏗️ Project Structure

```
fastapi-app/
├── app/                          # Main application code
│   ├── api/
│   │   ├── endpoints/           # API route handlers
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   ├── users.py        # User management
│   │   │   ├── products.py     # Product catalog
│   │   │   ├── cart.py         # Shopping cart
│   │   │   ├── orders.py       # Order processing & payments
│   │   │   └── ...             # Other endpoints
│   │   ├── deps.py             # Dependencies & auth
│   │   └── api.py              # Main API router
│   ├── core/
│   │   ├── config.py           # Configuration settings
│   │   └── security.py         # Security utilities
│   ├── crud/                    # Database operations
│   ├── db/                      # Database session management
│   ├── models/                  # SQLAlchemy ORM models
│   ├── schemas/                 # Pydantic validation schemas
│   └── services/                # Business logic (Stripe, etc.)
│
├── docs/                         # 📚 Documentation
│   ├── README.md                # Documentation index
│   ├── API_DOCEMENTATION.md     # Complete API reference
│   ├── DOCKER_DEPLOYMENT.md     # Docker guide
│   ├── STRIPE_SETUP_GUIDE.md    # Payment setup
│   ├── FRONTEND_INTEGRATION_GUIDE.md
│   └── ...                      # Other guides
│
├── scripts/                      # 🛠️ Utility scripts
│   ├── seed_products_bulk.py    # Bulk product seeding
│   ├── seed_production.py       # Production data seeding
│   ├── deploy.py                # Deployment automation
│   ├── start.sh                 # Application startup
│   └── utils/                   # Database & setup utilities
│       ├── create_admin.py      # Create admin user
│       ├── create_db.py         # Database creation
│       ├── fix_*.py             # Database fixes
│       └── setup_*.sh           # Setup scripts
│
├── tests/                        # 🧪 Test suite
│   ├── test_api.py              # API endpoint tests
│   ├── test_auth_fix.py         # Authentication tests
│   ├── test_stripe_payment.py   # Payment tests
│   ├── test_complete_order_flow.py
│   ├── check_*.py               # Validation scripts
│   └── ...                      # Other tests
│
├── alembic/                      # Database migrations
│   ├── versions/                # Migration files
│   └── env.py                   # Alembic config
│
├── .github/                      # GitHub Actions CI/CD
│   └── workflows/
│       └── deploy-fastapi.yml   # Deployment workflow
│
├── main.py                       # FastAPI application entry
├── requirements.txt              # Python dependencies
├── docker-compose.yml            # Docker Compose config
├── Dockerfile                    # Docker image definition
├── alembic.ini                   # Alembic configuration
├── pytest.ini                    # Pytest configuration
├── PROJECT_STRUCTURE.md          # Detailed structure guide
└── README.md                     # This file
```

> 📖 For detailed structure information, see [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)

## 🚀 Deployment

### 🐳 Docker Deployment (Recommended)

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

### 🤖 Automated Deployment (GitHub Actions)

The project includes a complete CI/CD pipeline:

```yaml
# .github/workflows/deploy-fastapi.yml
# Triggers on push to main branch
# - Builds Docker image
# - Runs database migrations
# - Deploys to production
# - Restarts application
```

### 🔧 Manual Production Deployment

```bash
# 1. Pull latest code
git pull origin main

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run deployment script (handles DB migrations)
python scripts/deploy.py

# 4. Start application
./scripts/start.sh
```

### 🌐 Production Setup

**Live API**: [https://fastapi.kevinlinportfolio.com](https://fastapi.kevinlinportfolio.com)

Production environment uses:
- **Nginx** as reverse proxy
- **PostgreSQL** on dedicated server
- **PM2** for process management
- **Let's Encrypt** for SSL certificates
- **GitHub Actions** for automated deployments

### 🔑 Environment Setup

```bash
# Copy production environment template
cp .env.example .env.production

# Configure production variables
nano .env.production
```

### 📊 Health Monitoring

```bash
# Check API health
curl https://fastapi.kevinlinportfolio.com/health

# View application logs
pm2 logs fastapi-app

# Check database connection
python tests/db_test.py
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

## � Seeding Data

### Bulk Product Seeding

Populate your database with realistic test data:

```bash
# Seed products in bulk (local)
python scripts/seed_products_bulk.py
# Enter number of products: 100

# Seed production database
python scripts/seed_production.py
```

Features:
- ✅ 50+ product images from Unsplash
- ✅ Realistic product names and descriptions
- ✅ Category-based pricing
- ✅ Stock quantities and variations
- ✅ Organic and featured product flags

### Create Admin User

```bash
# Create admin account
python scripts/utils/create_admin.py
```

### Clear Database

```bash
# Clear all products
python scripts/clear_all_products.py

# Clean bulk products
python scripts/clean_bulk_products.py
```

## � Documentation

### API Documentation

The API is fully documented with interactive Swagger UI:

- **📱 Interactive Docs (Swagger)**: http://localhost:8000/docs
- **📘 Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **📄 OpenAPI Schema**: http://localhost:8000/openapi.json
- **🏥 Health Check**: http://localhost:8000/health

### Project Documentation

Comprehensive guides in the [`/docs`](./docs) folder:

- **[API Documentation](./docs/API_DOCEMENTATION.md)** - Complete endpoint reference
- **[Docker Deployment Guide](./docs/DOCKER_DEPLOYMENT.md)** - Containerization setup
- **[Stripe Setup Guide](./docs/STRIPE_SETUP_GUIDE.md)** - Payment integration
- **[Frontend Integration](./docs/FRONTEND_INTEGRATION_GUIDE.md)** - Connect your frontend
- **[Project Structure](./PROJECT_STRUCTURE.md)** - Detailed file organization

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Production URLs

- **API Base**: https://fastapi.kevinlinportfolio.com/api/v1
- **Interactive Docs**: https://fastapi.kevinlinportfolio.com/docs
- **Health Check**: https://fastapi.kevinlinportfolio.com/health

## 📈 Performance & Scalability

- ⚡ **Async/Await**: Leveraging FastAPI's async capabilities
- 🔄 **Database Connection Pooling**: Efficient resource management
- 📦 **Pagination**: All list endpoints support pagination
- 🎯 **Indexed Queries**: Optimized database queries
- 🚀 **Production Ready**: Battle-tested in live environment

## 🛡️ Security Features

- 🔐 **JWT Tokens**: Secure, stateless authentication
- 🔒 **Password Hashing**: Bcrypt with salt
- 🛑 **CORS Protection**: Configurable origins
- ✅ **Input Validation**: Pydantic schemas on all endpoints
- 🔑 **API Key Support**: For service-to-service communication
- 🎫 **Role-Based Access**: Admin/User permissions

##  Roadmap

- [ ] GraphQL API support
- [ ] Real-time inventory updates (WebSockets)
- [ ] Advanced product recommendations
- [ ] Multi-language support (i18n)
- [ ] Image upload and management
- [ ] Email notification system
- [ ] Analytics and reporting dashboard

---

**Built with ❤️ using FastAPI, PostgreSQL, Stripe, and modern Python practices**

*Production-ready e-commerce API powering online businesses* 🚀

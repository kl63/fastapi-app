# FastAPI Boilerplate

A modern FastAPI boilerplate with SQLAlchemy ORM, JWT authentication, Alembic migrations, and comprehensive testing setup.

## Features

- **FastAPI Framework**: High-performance API framework with automatic Swagger/ReDoc documentation
- **SQLAlchemy ORM**: Database ORM with support for SQLite (dev) and PostgreSQL (production)
- **Alembic Migrations**: Database versioning and migration system
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control**: Admin and regular user permissions
- **Pydantic Models**: Type validation and settings management
- **Testing Suite**: Pytest fixtures for API and database testing
- **Environment Configuration**: .env file support for different environments

## Project Structure

```
fastapi-app/
│
├── alembic/                  # Database migrations
├── app/                      # Application package
│   ├── api/                  # API endpoints
│   │   ├── v1/               # API version 1
│   │   │   ├── endpoints/    # API route handlers
│   │   │   └── api.py        # API router
│   │   └── deps.py           # API dependencies
│   ├── core/                 # Core functionality
│   │   ├── config.py         # Settings and configuration
│   │   └── security.py       # Security utilities (JWT, password hashing)
│   ├── crud/                 # CRUD operations
│   │   └── user.py           # User CRUD operations
│   ├── db/                   # Database setup
│   │   ├── base.py           # Import models for Alembic
│   │   ├── base_class.py     # Base model class
│   │   └── session.py        # Database session management
│   ├── models/               # SQLAlchemy models
│   │   └── user.py           # User model
│   ├── schemas/              # Pydantic schemas
│   │   ├── token.py          # Token schemas
│   │   └── user.py           # User schemas
│   └── utils/                # Utility functions
│       └── pagination.py     # Pagination utilities
├── tests/                    # Test package
│   ├── api/                  # API tests
│   │   └── v1/               # API v1 tests
│   │       └── test_auth.py  # Authentication tests
│   └── conftest.py           # Test fixtures
├── .env.example              # Example environment variables
├── alembic.ini               # Alembic configuration
├── main.py                   # Application entry point
├── pytest.ini                # Pytest configuration
├── requirements.txt          # Project dependencies
└── setup.py                  # Package setup for dev installation
```

## Getting Started

### Prerequisites

- Python 3.9+
- pip (Python package installer)
- Virtual environment tool (venv, virtualenv, etc.)

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd fastapi-app
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file from the example:
   ```
   cp .env.example .env
   ```
   
5. Install the package in development mode:
   ```
   pip install -e .
   ```

### Database Setup

1. Initialize the database and run migrations:
   ```
   alembic upgrade head
   ```

### Running the Application

Run the application with Uvicorn:
```
uvicorn main:app --reload
```

Access the API documentation at:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

### Running Tests

Run the tests using pytest:
```
pytest
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login and get JWT token
- `POST /api/v1/auth/register` - Register a new user

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PATCH /api/v1/users/me` - Update current user profile
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PATCH /api/v1/users/{user_id}` - Update user (admin only)
- `GET /api/v1/users/` - List all users (admin only)

## Development

### Creating a new migration

After making changes to SQLAlchemy models, create a new migration:
```
alembic revision --autogenerate -m "Description of changes"
```

Then apply the migration:
```
alembic upgrade head
```

### Adding a new API endpoint

1. Create a new file in `app/api/v1/endpoints/`
2. Create a router and endpoints in the file
3. Add the router to `app/api/v1/api.py`

## License

This project is licensed under the MIT License.

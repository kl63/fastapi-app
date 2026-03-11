# Project Structure

This document describes the organization of the FastAPI E-commerce application.

## Root Directory

```
fastapi-app/
├── app/                    # Main application code
├── alembic/               # Database migrations
├── docs/                  # Documentation files
├── scripts/               # Utility and seeding scripts
├── tests/                 # Test files
├── venv/                  # Python virtual environment
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Docker compose configuration
├── Dockerfile            # Docker image definition
├── alembic.ini           # Alembic migration config
├── pytest.ini            # Pytest configuration
└── README.md             # Main project documentation
```

## Directory Details

### `/app` - Application Code
Contains all FastAPI application code including:
- `api/` - API endpoints and routes
- `models/` - SQLAlchemy database models
- `schemas/` - Pydantic validation schemas
- `crud/` - Database CRUD operations
- `core/` - Core configuration and utilities
- `db/` - Database connection and session management

### `/docs` - Documentation
All project documentation files:
- `API_DOCEMENTATION.md` - Complete API reference
- `DOCKER_DEPLOYMENT.md` - Docker deployment guide
- `FRONTEND_INTEGRATION_GUIDE.md` - Frontend integration guide
- `STRIPE_SETUP_GUIDE.md` - Payment setup guide
- `BACKEND_FIX_COMPLETE.md` - Backend fixes documentation
- `PRODUCTION_MIGRATION_FIX.md` - Production migration notes
- `README.md` - Documentation index

### `/scripts` - Utility Scripts
Production and development scripts:
- `seed_products_bulk.py` - Bulk product seeding
- `seed_production.py` - Production data seeding
- `deploy.py` - Deployment automation
- `start.sh` - Application startup script
- `utils/` - Utility scripts for database setup, fixes, and admin tasks

### `/tests` - Test Files
All test and validation scripts:
- `test_*.py` - Unit and integration tests
- `check_*.py` - Validation and verification scripts
- `*_test.py` - Additional test files
- `db_test.py` - Database connection tests

### `/alembic` - Database Migrations
Alembic migration scripts and version history for database schema management.

## Key Files

- **`main.py`** - FastAPI application entry point
- **`requirements.txt`** - Python package dependencies
- **`docker-compose.yml`** - Multi-container Docker configuration
- **`Dockerfile`** - Container image definition
- **`.env`** - Environment variables (not in version control)
- **`.env.example`** - Example environment configuration

## Development Workflow

1. **Setup**: Run scripts in `/scripts/utils/` for initial database and admin setup
2. **Development**: Work in `/app` directory with hot reload via uvicorn
3. **Testing**: Run tests from `/tests` directory using pytest
4. **Seeding**: Use scripts in `/scripts` to populate database
5. **Migration**: Use alembic commands to manage database schema
6. **Deployment**: Use Docker files and deployment scripts

## Documentation

- Main documentation is in `/docs` folder
- API documentation available at `/docs` endpoint when server is running
- See `/docs/README.md` for complete documentation index

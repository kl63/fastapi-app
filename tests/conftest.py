import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.models.user import User
from app.core.security import get_password_hash
from app import main

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_engine():
    """
    Create test database engine and tables
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Drop all tables after tests
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    Create a fresh database session for each test
    """
    # Connect to database
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    # Close and rollback session after test
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a FastAPI TestClient with DB session override
    """
    # Override the get_db dependency in the app
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    main.app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(main.app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def admin_user(db_session):
    """
    Create an admin user for testing
    """
    user = User(
        id="admin-test-id",
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("adminpassword"),
        full_name="Admin User",
        is_active=True,
        is_admin=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    return user


@pytest.fixture(scope="function")
def normal_user(db_session):
    """
    Create a normal user for testing
    """
    user = User(
        id="normal-test-id",
        email="user@example.com",
        username="normaluser",
        hashed_password=get_password_hash("userpassword"),
        full_name="Normal User",
        is_active=True,
        is_admin=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    return user

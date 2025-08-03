import logging
import uuid
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.base import Base
from app.db.session import engine
from app.core.security import get_password_hash
from app.models.user import User


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db() -> None:
    """
    Initialize database with tables and create initial admin user
    """
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Check if admin user already exists
    admin_user = db.query(User).filter(User.username == "admin").first()
    
    if not admin_user:
        # Create admin user
        admin_id = str(uuid.uuid4())
        admin_user = User(
            id=admin_id,
            email="admin@example.com",
            username="admin",
            hashed_password=get_password_hash("admin"),  # Change this in production
            full_name="Administrator",
            is_active=True,
            is_admin=True,
        )
        db.add(admin_user)
        db.commit()
        logger.info("Created admin user")
    else:
        logger.info("Admin user already exists")
    
    db.close()


if __name__ == "__main__":
    logger.info("Initializing database")
    init_db()
    logger.info("Database initialized successfully")

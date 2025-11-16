from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Boilerplate"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "FastAPI Boilerplate with SQLAlchemy, JWT Authentication, and Alembic"
    API_V1_STR: str = "/api/v1"

    # Secret key for JWT
    SECRET_KEY: str = "supersecretkey"  # ⚠️ Change this in production!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost",
        "https://freshcart.kevinlinportfolio.com",
        "https://fastapi.kevinlinportfolio.com"
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # ✅ Let BaseSettings pull DATABASE_URL from environment
    DATABASE_URL: str
    
    # Stripe Configuration (Backend Only - NEVER expose secret key to frontend)
    STRIPE_SECRET_KEY: str = ""  # Required: Set in .env file
    STRIPE_PUBLISHABLE_KEY: str = ""  # Optional: For reference, safe to expose to frontend
    STRIPE_WEBHOOK_SECRET: str = ""  # Required: For webhook signature verification

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


# Instantiate the settings object
settings = Settings()

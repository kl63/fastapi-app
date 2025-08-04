from typing import List, Optional, Union
import urllib.parse
from pydantic import AnyHttpUrl, validator, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Boilerplate"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "FastAPI Boilerplate with SQLAlchemy, JWT Authentication, and Alembic"
    API_V1_STR: str = "/api/v1"
    
    # Secret key for JWT
    SECRET_KEY: str = "supersecretkey"  # Change in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000", "http://localhost"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database settings - individual components
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    POSTGRES_HOST: Optional[str] = "localhost"
    POSTGRES_PORT: Optional[str] = "5432"
    
    # Database URL (can be overridden directly)
    DATABASE_URL: Optional[str] = None
    
    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_url(cls, v: Optional[str], info) -> str:
        if v:
            return v
            
        # Get values from the model
        values = info.data
        user = values.get("POSTGRES_USER")
        password = values.get("POSTGRES_PASSWORD")
        host = values.get("POSTGRES_HOST", "localhost")
        port = values.get("POSTGRES_PORT")
        
        # Ensure port is not empty and is valid
        if not port or port == "":
            port = "5432"  # Default PostgreSQL port
        
        db = values.get("POSTGRES_DB")
        
        if user and password and db:
            # URL encode the password in case it contains special characters
            encoded_password = urllib.parse.quote_plus(password)
            return f"postgresql://{user}:{encoded_password}@{host}:{port}/{db}"
            
        # Fallback to SQLite
        return "sqlite:///./app.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # Allow extra fields to prevent validation errors when new env vars are added
        extra = "ignore"


# Create settings instance
settings = Settings()

import uvicorn
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from sqlalchemy import text

from app.api.api import api_router
from app.core.config import settings
from app.db.session import engine, SessionLocal

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Set CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to FastAPI Boilerplate API",
        "version": settings.VERSION,
        "documentation": "/docs",
    }

# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    # Check database connection
    db_status = "healthy"
    start_time = time.time()
    db_response_time = 0
    
    try:
        # Don't use SQLAlchemy for health check to avoid greenlet issues
        # Instead use direct psycopg2 connection
        import psycopg2
        from urllib.parse import urlparse
        
        # Parse DATABASE_URL to get connection parameters
        if settings.DATABASE_URL.startswith('postgresql'):
            parsed = urlparse(settings.DATABASE_URL)
            dbname = parsed.path.lstrip('/')
            user = parsed.username
            password = parsed.password
            host = parsed.hostname
            port = parsed.port or 5432
            
            # Connect directly with psycopg2
            conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port
            )
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.close()
            conn.close()
        else:
            # Fallback to SQLAlchemy for SQLite or other DBs
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            
        db_response_time = round((time.time() - start_time) * 1000, 2)  # in ms
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    health_status = {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "timestamp": time.time(),
        "services": {
            "database": {
                "status": db_status,
                "response_time_ms": db_response_time
            },
            "api": {
                "status": "healthy"
            }
        },
        "version": settings.VERSION
    }
    
    # Return with appropriate status code
    status_code = status.HTTP_200_OK if health_status["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(content=health_status, status_code=status_code)

# Include API router
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

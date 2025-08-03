from setuptools import setup, find_packages

setup(
    name="fastapi-app",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "alembic",
        "pydantic",
        "pydantic-settings",
        "python-jose",
        "passlib",
        "python-multipart",
        "email-validator",
        "bcrypt",
        "pytest",
        "httpx",
        "psycopg2-binary",
        "python-dotenv",
    ],
)

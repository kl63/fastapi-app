#!/usr/bin/env python3
import os
import sys
import logging
import subprocess
from urllib.parse import urlparse, unquote

import psycopg2


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
log = logging.getLogger(__name__)


def mask_db_url(db_url: str) -> str:
    """Return DATABASE_URL with password masked for logs."""
    try:
        u = urlparse(db_url)
        if not u.scheme:
            return "***"
        user = u.username or ""
        host = u.hostname or ""
        port = u.port or ""
        dbname = (u.path or "").lstrip("/")
        return f"{u.scheme}://{user}:***@{host}:{port}/{dbname}"
    except Exception:
        return "***"


def parse_database_url(db_url: str):
    """
    Parse DATABASE_URL and DECODE username/password (critical for %40 etc).
    Example:
      postgresql://user:%40pass@127.0.0.1:5432/db
    """
    if not db_url:
        raise ValueError("DATABASE_URL is empty or not set")

    u = urlparse(db_url)

    if not u.scheme or not u.hostname:
        raise ValueError(f"Invalid DATABASE_URL (missing scheme/host): {mask_db_url(db_url)}")

    db_user = unquote(u.username or "")
    db_password = unquote(u.password or "")
    db_host = u.hostname or "127.0.0.1"
    db_port = u.port or 5432
    db_name = (u.path or "").lstrip("/")

    if not db_name:
        raise ValueError("Invalid DATABASE_URL (missing database name in path)")

    return db_user, db_password, db_host, db_port, db_name


def ensure_database_exists(db_user: str, db_password: str, db_host: str, db_port: int, db_name: str):
    """
    Connect to 'postgres' DB and create target db if it doesn't exist.
    Requires the user to have permission to create databases.
    """
    log.info("Checking if database '%s' exists on %s:%s", db_name, db_host, db_port)

    conn = psycopg2.connect(
        dbname="postgres",
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        connect_timeout=5,
        sslmode="prefer",
    )
    conn.autocommit = True

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (db_name,))
            exists = cur.fetchone() is not None

            if exists:
                log.info("Database '%s' already exists.", db_name)
                return

            log.info("Database '%s' does not exist. Creating...", db_name)
            # Use identifier safely (dbname cannot be a parameter in CREATE DATABASE)
            cur.execute(f'CREATE DATABASE "{db_name}";')
            log.info("Database '%s' created successfully.", db_name)
    finally:
        conn.close()


def run_alembic_upgrade():
    """
    Runs: alembic upgrade head
    Assumes alembic.ini is in project root (current working directory).
    """
    log.info("Running Alembic migrations: alembic upgrade head")
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        check=False,
        text=True,
        capture_output=True,
        env=os.environ.copy(),
    )

    if result.stdout:
        log.info("alembic stdout:\n%s", result.stdout.strip())
    if result.stderr:
        # alembic writes some info to stderr sometimes; keep as warning
        log.warning("alembic stderr:\n%s", result.stderr.strip())

    if result.returncode != 0:
        raise RuntimeError(f"Alembic failed with exit code {result.returncode}")

    log.info("Alembic migrations completed.")


def main():
    try:
        db_url = os.getenv("DATABASE_URL", "")
        log.info("🔍 DEBUG: DATABASE_URL from env: %s", mask_db_url(db_url))

        db_user, db_password, db_host, db_port, db_name = parse_database_url(db_url)

        # Create DB if needed
        ensure_database_exists(db_user, db_password, db_host, db_port, db_name)

        # Run migrations
        run_alembic_upgrade()

        log.info("✅ Deployment steps completed successfully.")
        return 0

    except psycopg2.OperationalError as e:
        log.error("Database connection error: %s", str(e))
        return 1
    except Exception as e:
        log.error("Deployment error: %s", str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())

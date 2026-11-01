
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Load the project's .env file.
# Project root: PP/.env
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / "PP" / ".env"

load_dotenv(ENV_FILE)

# Read the PostgreSQL connection URL.
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        f"DATABASE_URL not found. Check your .env file at: {ENV_FILE}"
    )

# Create the database engine.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Create database sessions.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

# Base class for our database models.
class Base(DeclarativeBase):
    pass


# Dependency for FastAPI routes.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Test the database connection.
def test_connection():
    from sqlalchemy import text

    with engine.connect() as connection:
        result = connection.execute(text("SELECT version()"))
        print("PostgreSQL connected successfully!")
        print(result.scalar())


if __name__ == "__main__":
    test_connection()

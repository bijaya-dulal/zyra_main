# app/db.py
"""
Database Handshake File
-----------------------
This file handles:
1. Creating the SQLAlchemy engine
2. Creating the SessionLocal class for DB sessions
3. Creating the Base class for ORM models
4. Providing the get_db() dependency for FastAPI routes
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings


# -----------------------------
# DATABASE URL
# -----------------------------
DATABASE_URL = settings.DATABASE_URL  # Loaded from .env via Settings class


# -----------------------------
# SQLALCHEMY ENGINE
# -----------------------------
# echo=True shows SQL queries in terminal (enable during debugging)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
      echo=True,  # Ensures connections are alive
)


# -----------------------------
# SESSION LOCAL
# -----------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# -----------------------------
# BASE CLASS FOR MODELS
# -----------------------------
Base = declarative_base()


# -----------------------------
# FASTAPI DEPENDENCY
# -----------------------------
def get_db():
    """
    Dependency to get a database session.
    Automatically closes session after request is done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

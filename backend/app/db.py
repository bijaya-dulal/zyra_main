"""
Database Handshake File
-----------------------
This file handles:
1. Creating the Base class for ORM models (Declarative Base).
2. Creating the SQLAlchemy Asynchronous engine.
3. Creating the AsyncSession maker for sessions.
4. Providing the get_db() dependency for FastAPI routes.
5. Providing the init_db() function to create all tables.
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings # Assuming core.config is now app.config

# -----------------------------
# BASE CLASS FOR MODELS
# -----------------------------
# This is the base class that all your SQLAlchemy models (Subject, Document, etc.)
# will inherit from. It registers the models with the database metadata.
Base = declarative_base()


# -----------------------------
# SQLALCHEMY ASYNC ENGINE
# -----------------------------
# Uses the URL defined in settings.py. Async engine for non-blocking operations.
# echo=True shows SQL queries in terminal (enable during debugging)
engine = create_async_engine(
    settings.DATABASE_URL, 
    echo=settings.ENV == "development" # Only show SQL in development
)


# -----------------------------
# ASYNCHRONOUS SESSION MAKER
# -----------------------------
# Creates a configured "factory" for AsyncSession objects.
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False, # Prevents objects from being detached after commit
    autocommit=False,
    autoflush=False
)


# -----------------------------
# FASTAPI DEPENDENCY
# -----------------------------
async def get_db():
    """
    Dependency to get an asynchronous database session.
    Automatically closes the session after the request is done.
    """
    async with AsyncSessionLocal() as session:
        yield session


# -----------------------------
# DATABASE INITIALIZATION
# -----------------------------
async def init_db():
    """
    Function to create all tables defined in Base.metadata.
    Called once during application startup.
    """
    # This block is used when you first set up the database.
    # We use engine.begin() for a transactional operation.
    async with engine.begin() as conn:
        # conn.run_sync() is used to run synchronous ORM operations (like create_all)
        # on the asynchronous connection.
        await conn.run_sync(Base.metadata.create_all)
    
    # NOTE: You should rely on Alembic for migrations, not repeated create_all calls.
    # However, this is useful for initial setup and testing.
# app/config.py
"""
Settings / Environment Manager
-------------------------------
This file loads all environment variables required by the project.

It manages:
- DATABASE_URL
- VECTOR_DB_URL
- API keys (OpenAI, HuggingFace, etc.)
- Any other config values

Pydantic BaseSettings automatically reads from:
- .env file
- OS environment variables
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
   
    # PROJECT CONFIG

    # New Setting: Name of the Project
    PROJECT_NAME: str = "zyra_rag_System"

    # -----------------------------
    # DATABASE CONFIG
    # -----------------------------
    # Required setting: will load from environment variable or .env
    DATABASE_URL: str = "DATABASE_URL=postgresql+asyncpg://bijaya:bijaya201542@localhost:5432/zyra_rag"
    
    
    # Optional setting, falls back to the main DB if not set
    VECTOR_DB_URL: str | None = None  

    # -----------------------------
    # LLM & EMBEDDING CONFIG

    # New Setting: Default embedding model name
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Existing Setting: LLM API Keys
    OPENAI_API_KEY: str | None = None
    HUGGINGFACE_API_KEY: str | None = None

    # -----------------------------
    # ENVIRONMENT MODE/production mode

    ENV: str = "development"   #this should be chaged to the production after go tho production for the production phase


    class Config:
        env_file = ".env"  # Loads variables from .env


# Cached so it's loaded only once for performance
@lru_cache()
def get_settings():
    """Initializes and returns a cached Settings object."""
    return Settings()


# Final settings object used throughout the application
settings = get_settings()
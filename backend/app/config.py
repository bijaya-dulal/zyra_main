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
    # -----------------------------
    # DATABASE CONFIG
    # -----------------------------
    DATABASE_URL: str = "postgresql+psycopg2://postgres:bijaya201542@localhost/zyra_rag"

    # For pgvector, pinecone, chroma, etc.
    VECTOR_DB_URL: str = "postgresql+psycopg2://postgres:bijaya201542@localhost/zyra_rag"  

    # -----------------------------
    # LLM API KEYS
    # -----------------------------
    OPENAI_API_KEY: str | None = None
    HUGGINGFACE_API_KEY: str | None = None

    # -----------------------------
    # ENVIRONMENT MODE
    # -----------------------------
    ENV: str = "development"   

    class Config:
        env_file = ".env"  # Loads variables from .env


# Cached so it's loaded only once
@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()

import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # PROJECT CONFIG
    PROJECT_NAME: str = "zyra_rag_System"

    # -----------------------------
    # DATABASE CONFIG
    # -----------------------------
    # FIX 1: Removed "DATABASE_URL=" prefix. 
    # SQLAlchemy needs just the URL, not the key name.
    DATABASE_URL: str = "postgresql+asyncpg://bijaya:bijaya201542@localhost:5432/zyra_rag"
    
    VECTOR_DB_URL: str | None = None  

    # -----------------------------
    # OAuth configuration
    # -----------------------------
    # FIX 2: Removed os.getenv(). 
    # Pydantic automatically looks for "SECRET_KEY" in your .env file.
    # If you use os.getenv, it runs BEFORE Pydantic loads the .env file, often resulting in empty values.
    SECRET_KEY: str = "super_secret_random_string_here" 
    
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # FIX 3: Removed os.getenv(). Pydantic will read these from .env automatically.
    # If not found in .env, it uses these strings as defaults.
    GOOGLE_CLIENT_ID: str 
    GOOGLE_CLIENT_SECRET: str 
    
    # FIX 4: Changed localhost to 127.0.0.1 to match your previous Google Auth Fix
    GOOGLE_REDIRECT_URI: str = "http://127.0.0.1:8000/api/v1/auth/google/callback"

    # -----------------------------
    # LLM & EMBEDDING CONFIG
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    OPENAI_API_KEY: str | None = None
    HUGGINGFACE_API_KEY: str | None = None

    ENV: str = "development"

    # This is the line that makes the magic happen
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
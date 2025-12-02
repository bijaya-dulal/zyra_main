"""
The main gate of your backend.

Tasks:
- Initializes the FastAPI app with project settings.
- Configures necessary middleware (CORS).
- Includes all API routers (v1).
- Defines lifecycle events (DB startup).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter # Required topic: Define root endpoints cleanly

# Assuming your config is now accessible this way:
from app.core.config import settings

# Database Initialization
# Assuming your db init function is in a file named 'db.py' or 'app/db.py'
from app.db import init_db 

# Application Routers
# Assuming all your routers are correctly defined in app/routers/v1
from app.routers.v1 import subjects, documents, chunks, embeddings, rag, exams


def create_application() -> FastAPI:
    # -----------------------------
    # 1. Starts the FastAPI app
    # -----------------------------
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="FastAPI service for the Student RAG System (Retrieval-Augmented Generation).",
        # Custom docs URL is often useful in production
        docs_url="/docs" if settings.ENV == "development" else None,
        redoc_url="/redoc" if settings.ENV == "development" else None,
    )

    # -----------------------------
    # 2. Configure Middleware
    # -----------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins for development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -----------------------------
    # 3. Register Routers
    # -----------------------------
    app.include_router(subjects.router, prefix="/api/v1/subjects", tags=["Subjects"])
    app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
    app.include_router(chunks.router, prefix="/api/v1/chunks", tags=["Chunks"])
    app.include_router(embeddings.router, prefix="/api/v1/embeddings", tags=["Embeddings"])
    app.include_router(rag.router, prefix="/api/v1/rag", tags=["RAG"])
    app.include_router(exams.router, prefix="/api/v1/exams", tags=["Exams"])


    return app


# Create the core application instance
app = create_application()


# -----------------------------
# 4. Define Root Endpoints
# -----------------------------
@app.get("/", tags=["Status"])
async def root():
    """Returns basic API status and project information."""
    return {
        "project_name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "status": "active",
        "environment": settings.ENV,
    }
 

# -----------------------------
# 5. Lifecycle Events (Startup/Shutdown)
# -----------------------------
@app.on_event("startup")
async def startup_event():
    """Run database initialization on application startup."""
    print("Initializing Database Connection...")
    await init_db()
    print("Database Initialization Complete.")


# -----------------------------
# Unused Section: Runs the server
# -----------------------------
# NOTE: The server is typically run using the uvicorn command line.
# Example: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# The server startup code is not needed here.
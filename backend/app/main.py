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
from fastapi.responses import HTMLResponse # ADDED: HTMLResponse import

# Assuming your config is now accessible this way:
from app.core.config import settings

# Database Initialization
# Assuming your db init function is in a file named 'db.py' or 'app/db.py'
from app.db import init_db 

# Application Routers
# Assuming all your routers are correctly defined in app/routers/v1
from app.routers.v1 import subjects, documents, chunks, embeddings, rag, exams

# --- Helper Function to Create the HTML Content ---
def generate_welcome_html(status_data: dict) -> str:
    """Generates a responsive HTML page embedding application status."""

    # Format the status data into an HTML list for display
    status_items = "".join([
        f'<li class="text-gray-300"><span class="font-semibold text-white">{key.replace("_", " ").title()}:</span> {value}</li>'
        for key, value in status_data.items()
    ])

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZYRA AI Teacher</title>
    <!-- Tailwind CSS CDN for easy styling -->
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        body {{
            font-family: 'Inter', sans-serif;
            background-color: #0d1117; /* Dark background */
        }}
    </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4">
    <div class="max-w-4xl w-full bg-[#161b22] border border-[#30363d] rounded-xl shadow-2xl p-8 md:p-12">
        
        <!-- Main Header and Welcome -->
        <header class="text-center mb-10">
            <h1 class="text-4xl md:text-5xl font-extrabold text-[#58a6ff] mb-2">
                Welcome to ZYRA
            </h1>
            <p class="text-xl md:text-2xl text-white font-light mt-4 leading-relaxed">
                🇳🇵 The First AI Teacher in Nepal 🇳🇵
            </p>
        </header>

        <!-- Description/Mission -->
        <section class="mb-10">
            <p class="text-lg text-gray-400 text-center">
                ZYRA is your next-generation knowledge assistant, dedicated to providing educational resources 
                and support across various subjects, powered by a robust and reliable FastAPI backend.
            </p>
        </section>

        <!-- Status Card -->
        <section class="bg-[#21262d] p-6 rounded-lg border border-[#30363d]">
            <h2 class="text-2xl font-semibold text-white border-b border-gray-600 pb-3 mb-4">
                System Status Overview
            </h2>
            <ul class="space-y-2 text-md">
                {status_items}
            </ul>
        </section>

        <!-- API Links Hint -->
        <footer class="mt-10 text-center text-sm text-gray-500">
            Access the interactive API documentation at: <a href="/docs" class="text-[#58a6ff] hover:underline">/docs</a>
        </footer>
    </div>
</body>
</html>
    """
    return html_content


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
@app.get("/", tags=["Status"], response_class=HTMLResponse) # ADDED: response_class=HTMLResponse
async def root():
    """Returns the welcome page with application status."""
    
    # 1. Gather application status data (from the original JSON structure)
    status_data = {
        "project_name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "status": "active",
        "environment": settings.ENV
    }
    
    # 2. Generate the HTML content using the status data
    html_content = generate_welcome_html(status_data)
    
    # 3. Return the HTML as the response
    return HTMLResponse(content=html_content, status_code=200)
 

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
# ZYRA Backend: AI Agent Instructions

ZYRA is an educational RAG system with an **asynchronous FastAPI backend** designed for document ingestion, semantic chunking, and vector-based retrieval.

## Architecture Overview

### Core Data Flow
**Exams → Subjects → Documents → Chunks → Embeddings**

Each exam contains multiple subjects; each subject contains documents; each document is chunked into semantic pieces; each chunk gets embedded into a 1536-dimensional vector.

### Key Modules

- **`app/db.py`** – Async SQLAlchemy engine, session factory (`AsyncSessionLocal`), and `get_db()` dependency
- **`app/models/`** – ORM models (Exam, Subject, Document, Chunk, Embedding, Uploader)
- **`app/services/`** – Business logic using `Async*Service` pattern (e.g., `AsyncSubjectService`)
- **`app/routers/v1/`** – FastAPI endpoint handlers prefixed with `/api/v1/`
- **`app/schemas/`** – Pydantic v2 validation models
- **`app/core/config.py`** – Settings from `.env` (DATABASE_URL, EMBEDDING_MODEL, API keys)

## Critical Development Patterns

### Async/Await Convention
All service methods are `async`. Routes call them with `await`. Use `run_in_threadpool()` for blocking I/O:

```python
from fastapi.concurrency import run_in_threadpool

saved_path = await run_in_threadpool(
    LocalStorage.save_file, file_name, file_bytes
)
```

### Pydantic v2 Usage
- Use `model_dump()` (not `dict()`) for schema to dict conversion
- Use `orm_mode = True` (or `from_attributes = True`) for ORM deserialization
- Import from `pydantic` not `pydantic.v1`

### Service Layer Pattern
Services are static classes with async methods:

```python
class AsyncSubjectService:
    @staticmethod
    async def list_subjects(db: AsyncSession, limit: int = 20, offset: int = 0):
        stmt = select(Subject).offset(offset).limit(limit)
        result = await db.scalars(stmt)
        return result.all()
```

### Database Dependency
Always inject `db: AsyncSession = Depends(get_db)` in routes:

```python
@router.get("/", response_model=list[SubjectResponse])
async def list_subjects(db: AsyncSession = Depends(get_db)):
    return await AsyncSubjectService.list_subjects(db)
```

## Document Processing Pipeline

**Key file:** `app/services/extractor/pipeline.py`

1. **File Storage** – Local filesystem (`storage/documents/` path) via `LocalStorage` class
2. **Extraction** – `ExtractionPipeline.extract()` routes by subject:
   - Math/Account docs → Nougat (currently disabled due to instability)
   - Other docs → Docling/SimplePDFExtractor (fallback)
3. **Chunking** – `AcademicChunker` preserves formulas, tables, headings; respects semantic boundaries
4. **Return Format** – `{"raw_text": str, "markdown": str, "meta": dict}`

### Text Splitter Strategy
Formulas are protected, abbreviations preserved. Academic content respects section boundaries. Max chunk tokens: 512 (configurable).

## Database Migrations

Use **Alembic** (not `create_all()`):

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

Migration config: `backend/alembic.ini` (synchronous psycopg2 URL for Alembic)
Runtime URL: async with `postgresql+asyncpg://...` in `app/core/config.py`

## Configuration & Environment

Settings flow: `.env` → `pydantic_settings.BaseSettings` → `app/core/config.py` → injected via `settings`

Example `.env`:
```
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/zyra_rag
EMBEDDING_MODEL=text-embedding-3-small
ENV=development
OPENAI_API_KEY=sk-...
```

## Server Startup

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Root endpoint (`/`) returns styled HTML status page with FastAPI docs at `/docs`.

## Common Workflows

### Add a New Entity Type
1. Create model in `app/models/new_entity.py` inheriting `Base`
2. Create schema in `app/schemas/new_entity_schemas.py` (Create, Update, Response)
3. Create service `AsyncNewEntityService` in `app/services/new_entity_service.py`
4. Create router in `app/routers/v1/new_entity.py`, include in `app/main.py`
5. Run `alembic revision --autogenerate` to create migration

### Debug Service Logic
Services are testable in isolation. Call them directly in tests or add logging to the service method.

### Handle Cascading Deletes
Document deletion cascades to chunks; chunk deletion cascades to embeddings (via `ondelete="CASCADE"` in FK definitions).

## Known Constraints

- **Nougat extractor** disabled – falls back to SimplePDFExtractor; re-enable when environment stability improves
- **Vector embeddings** – pgvector extension required; 1536-dim vectors for OpenAI/LLaMA models
- **Async routers** – All routes must be `async def` to avoid blocking the event loop
- **Session management** – Do NOT create sessions manually; always use `get_db()` dependency

## Quick Reference

- **Start server:** `uvicorn app.main:app --reload`
- **Migrate DB:** `alembic upgrade head`
- **New migration:** `alembic revision --autogenerate -m "..."`
- **Run tests:** `pytest backend/` (if test suite exists)

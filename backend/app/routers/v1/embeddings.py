from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional

from app.db import get_db
from app.models.chunks import Chunk
from app.models.embeddings import Embedding
# We use the service we already verified instead of a new 'Pipeline' class
from app.services.embeddings.embeding_services import EmbeddingService 

router = APIRouter(prefix="/embeddings", tags=["Embeddings"])

class EmbeddingStatusResponse(BaseModel):
    document_id: str
    total_chunks: int
    embedded_chunks: int
    completion_percentage: float

@router.get("/document/{document_id}/status", response_model=EmbeddingStatusResponse)
async def get_embedding_status(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Check how many chunks in a document have been embedded.
    (Converted to Async for performance)
    """
    # 1. Count Total Chunks
    # SQL: SELECT count(*) FROM document_chunks WHERE document_id = ...
    stmt_total = select(func.count()).select_from(Chunk).where(Chunk.document_id == document_id)
    total_result = await db.execute(stmt_total)
    total_chunks = total_result.scalar() or 0
    
    # 2. Count Embedded Chunks (Chunks that have a matching Embedding record)
    # SQL: SELECT count(*) FROM chunk_embeddings JOIN document_chunks ...
    stmt_embedded = select(func.count()).select_from(Embedding)\
        .join(Chunk, Embedding.chunk_id == Chunk.id)\
        .where(Chunk.document_id == document_id)
    embedded_result = await db.execute(stmt_embedded)
    embedded_chunks = embedded_result.scalar() or 0
    
    return {
        "document_id": document_id,
        "total_chunks": total_chunks,
        "embedded_chunks": embedded_chunks,
        "completion_percentage": (embedded_chunks / total_chunks * 100) if total_chunks > 0 else 0.0
    }
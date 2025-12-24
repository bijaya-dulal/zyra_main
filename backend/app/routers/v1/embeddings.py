
# ============================================================================
# File: app/api/routes/embeddings.py
# API endpoints for embedding management
# ============================================================================
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.services.embeddings.embedding_pipeline import EmbeddingPipeline
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/embeddings", tags=["embeddings"])


class EmbeddingResponse(BaseModel):
    chunk_id: str
    embedding_id: str
    dimensions: int
    model_name: str


class ProcessDocumentRequest(BaseModel):
    document_id: str
    batch_size: Optional[int] = 32
    reprocess: Optional[bool] = False


@router.post("/process-document")
async def process_document_embeddings(
    request: ProcessDocumentRequest,
    db: Session = Depends(get_db)
):
    """Generate embeddings for all chunks in a document."""
    try:
        pipeline = EmbeddingPipeline(db)
        
        if request.reprocess:
            embeddings = pipeline.reprocess_document(
                request.document_id,
                batch_size=request.batch_size
            )
        else:
            embeddings = pipeline.process_document(
                request.document_id,
                batch_size=request.batch_size
            )
        
        return {
            "success": True,
            "document_id": request.document_id,
            "embeddings_created": len(embeddings),
            "model": pipeline.model_name,
            "dimensions": pipeline.dimensions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/document/{document_id}/status")
async def get_embedding_status(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Check embedding status for a document."""
    from app.models.chunks import Chunk
    from app.models.embeddings import Embedding
    
    # Count chunks
    total_chunks = db.query(Chunk).filter(
        Chunk.document_id == document_id
    ).count()
    
    # Count embeddings
    embedded_chunks = db.query(Embedding).join(
        Chunk, Embedding.chunk_id == Chunk.id
    ).filter(
        Chunk.document_id == document_id
    ).count()
    
    return {
        "document_id": document_id,
        "total_chunks": total_chunks,
        "embedded_chunks": embedded_chunks,
        "missing_embeddings": total_chunks - embedded_chunks,
        "completion_percentage": (embedded_chunks / total_chunks * 100) if total_chunks > 0 else 0
    }


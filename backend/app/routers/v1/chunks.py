from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.db import get_db
from app.models.chunks import Chunk
from pydantic import BaseModel

router = APIRouter(prefix="", tags=["Chunks (Debug)"])

# --- SCHEMAS ---
class ChunkResponse(BaseModel):
    id: str
    document_id: str
    chunk_index: int
    content: str
    token_count: int
    
    class Config:
        from_attributes = True

# --- ENDPOINTS ---

@router.get("/", response_model=List[ChunkResponse])
async def list_chunks(
    document_id: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),  # <--- ADDED THIS (Essential for pagination)
    db: AsyncSession = Depends(get_db)
):
    """
    View raw chunks. Use limit/offset to page through long documents.
    """
    stmt = select(Chunk)
    
    if document_id:
        stmt = stmt.where(Chunk.document_id == document_id)
        
    # Order by chunk_index to read the text in correct order
    stmt = stmt.order_by(Chunk.chunk_index).offset(offset).limit(limit)
    
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{chunk_id}", response_model=ChunkResponse)
async def get_chunk(
    chunk_id: str,
    db: AsyncSession = Depends(get_db)
):
    """View a specific chunk by its ID."""
    chunk = await db.get(Chunk, chunk_id)
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    return chunk
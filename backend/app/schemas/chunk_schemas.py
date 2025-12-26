from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChunkBase(BaseModel):
    """Base fields for a Document Chunk."""
    content: str
    chunk_index: int
    token_count: int
    chunk_type: Optional[str] = "text"
    start_index: Optional[int] = None
    end_index: Optional[int] = None
    meta_data: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ChunkCreate(ChunkBase):
    """Schema for creating a new chunk (includes the link to document)."""
    id: str = Field(..., description="Unique UUID for the chunk")
    document_id: str

class ChunkUpdate(BaseModel):
    """Schema for updating an existing chunk."""
    content: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None

class ChunkResponse(ChunkBase):
    """Schema for returning chunk data to the API."""
    id: str
    document_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class ChunkWithEmbedding(ChunkResponse):
    """Schema for returning chunk data along with its vector (useful for debugging)."""
    vector: List[float] = Field(..., alias="embedding_vector")
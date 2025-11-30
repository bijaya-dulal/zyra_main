from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ARRAY, DOUBLE_PRECISION
from app.db import Base
from pgvector.sqlalchemy import Vector # pyright: ignore[reportMissingImports]

class Embedding(Base):
    __tablename__ = "chunk_embeddings"

    id = Column(String, primary_key=True, index=True)

    # FK → delete embedding if chunk is deleted
    chunk_id = Column(
        String,
        ForeignKey("chunks.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,       # 1-to-1 relationship
        index=True
    )

    # Vector of floats (1536 dim for OpenAI / LLama embeddings)
    embedding_vector = Column(Vector(1536), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship back to Chunk
    chunk = relationship("Chunk", back_populates="embedding")

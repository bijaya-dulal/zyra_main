from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base


class Chunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True, index=True)

    # FK to Document (CASCADE so deleting a document deletes its chunks)
    document_id = Column(
        String,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    chunk_index = Column(Integer, nullable=False)   # ordering of chunks
    content = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    document = relationship("Document", back_populates="chunks")

    # 1-to-1 relationship (each chunk has exactly ONE embedding)
    embedding = relationship(
        "Embedding",
        back_populates="chunk",
        uselist=False,
        cascade="all, delete-orphan"
    )

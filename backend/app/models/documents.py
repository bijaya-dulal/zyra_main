from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)

    # Core metadata
    title = Column(Text, nullable=False)
    description = Column(Text)
    source = Column(String(50))  # pdf, web, youtube, etc.
    uri = Column(Text, nullable=False)
    language = Column(String(10), default="en")

    # Foreign keys
    uploader_id = Column(String, ForeignKey("uploaders.id", ondelete="SET NULL"))
    subject_id = Column(String, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)

    # Optional metadata
    tags = Column(ARRAY(Text))

    # Processing metadata
    version = Column(Integer, default=1)
    status = Column(String(20), default="active")  # active / archived / deleted

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    uploader = relationship("Uploader", back_populates="documents")
    subject = relationship("Subject", back_populates="documents")

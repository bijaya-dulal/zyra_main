from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)

    title = Column(Text, nullable=False)
    description = Column(Text)
    doc_type = Column(String(50))  # note, past question, summary
    uri = Column(Text, nullable=False)
    language = Column(String(10), default="en", index=True)

    uploader_id = Column(String, ForeignKey("uploaders.id", ondelete="SET NULL"))
    subject_id = Column(String, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)

    tags = Column(ARRAY(Text))

    version = Column(Integer, default=1)
    status = Column(String(20), default="active", index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    uploader = relationship("Uploader", back_populates="documents")
    subject = relationship("Subject", back_populates="documents")
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

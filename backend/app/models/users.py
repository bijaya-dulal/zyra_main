import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db import Base

class User(Base):
    __tablename__ = "users"

    # Primary Key
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Core Fields
    email = Column(String(150), unique=True, index=True, nullable=False)
    
    # ✅ CHANGED: We store 'hashed_password', not 'password'
    hashed_password = Column(String, nullable=True)
    
    # Google / Auth Fields
    provider = Column(String(50), default="local") # 'local' or 'google'
    picture = Column(String, nullable=True)        # To show their avatar
    
    full_name = Column(String(100), nullable=True)
    role = Column(String(20), default="student", nullable=False) # 'admin', 'teacher', 'student'
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    # Ensure "Document" model has relationship("User", back_populates="uploader")
    documents = relationship("Document", back_populates="uploader", passive_deletes=True)
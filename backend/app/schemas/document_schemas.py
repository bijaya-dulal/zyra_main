from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DocumentBase(BaseModel):
    title: str
    description: Optional[str] = None
    doc_type: Optional[str] = None
    uri: str
    language: Optional[str] = "en"
    uploader_id: Optional[str] = None
    subject_id: str
    tags: Optional[List[str]] = None
    version: Optional[int] = 1
    status: Optional[str] = "active"

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    doc_type: Optional[str] = None
    uri: Optional[str] = None
    language: Optional[str] = None
    uploader_id: Optional[str] = None
    subject_id: Optional[str] = None
    tags: Optional[List[str]] = None
    version: Optional[int] = None
    status: Optional[str] = None

class DocumentResponse(DocumentBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

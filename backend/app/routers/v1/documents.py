from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.document_service import AsyncDocumentService
from app.schemas.document_schemas import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse
)

router = APIRouter(prefix="", tags=["Documents"])

# Create
@router.post("/", response_model=DocumentResponse)
def create_doc(data: DocumentCreate, db: Session = Depends(get_db)):
    return AsyncDocumentService.create_document(db, data)

# List documents
@router.get("/", response_model=list[DocumentResponse])
async def list_docs(
    subject_id: str = None,
    doc_type: str = None,
    status: str = None,
    language: str = None,
    db: Session = Depends(get_db)
):
    return await AsyncDocumentService.list_documents(db, subject_id, doc_type, status, language)

# Get one
@router.get("/{doc_id}", response_model=DocumentResponse)
def get_doc(doc_id: str, db: Session = Depends(get_db)):
    doc = AsyncDocumentService.get_document(db, doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    return doc

# Update
@router.put("/{doc_id}", response_model=DocumentResponse)
def update_doc(doc_id: str, data: DocumentUpdate, db: Session = Depends(get_db)):
    doc = AsyncDocumentService.update_document(db, doc_id, data)
    if not doc:
        raise HTTPException(404, "Document not found")
    return doc

# Delete
@router.delete("/{doc_id}")
def remove_doc(doc_id: str, db: Session = Depends(get_db)):
    deleted = AsyncDocumentService.delete_document(db, doc_id)
    if not deleted:
        raise HTTPException(404, "Document not found")
    return {"message": "Document deleted successfully"}

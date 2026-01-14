from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db import get_db
from app.services.document_service import AsyncDocumentService
from app.schemas.document_schemas import DocumentCreate, DocumentUpdate, DocumentResponse

router = APIRouter(tags=["Documents"])

@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    subject_id: Optional[str] = None,
    doc_type: Optional[str] = None,
    limit: int = Query(20, ge=1),
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    return await AsyncDocumentService.list_documents(db, subject_id, doc_type, limit, offset)

@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: str, db: AsyncSession = Depends(get_db)):
    doc = await AsyncDocumentService.get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(data: DocumentCreate, db: AsyncSession = Depends(get_db)):
    # Note: This creates the METADATA. Use /ingest/process to upload the actual file content.
    return await AsyncDocumentService.create_document(db, data)

@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(doc_id: str, db: AsyncSession = Depends(get_db)):
    success = await AsyncDocumentService.delete_document(db, doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return None
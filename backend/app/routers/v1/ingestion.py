from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db import get_db
from app.services.document_service import AsyncDocumentService

router = APIRouter(prefix="/ingestion", tags=["Ingestion"])

class IngestRequest(BaseModel):
    document_id: str
    file_path: str
    subject_name: str

@router.post("/process")
async def process_document(
    request: IngestRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    1. Checks if document metadata exists.
    2. Starts the background task to Chunk, Embed, AND SAVE to DB.
    """
    # Verify the document ID exists in your metadata table first
    doc = await AsyncDocumentService.get_document(db, request.document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document ID not found. Please create document metadata first.")

    # ✅ CRITICAL FIX: Use the service method that INCLUDES saving to the DB
    # We use BackgroundTasks so the API doesn't freeze for 30 seconds
    background_tasks.add_task(
        AsyncDocumentService.process_and_finalize,
        db, 
        request.file_path, 
        request.subject_name, 
        request.document_id
    )
    
    return {
        "status": "processing_started", 
        "message": "Ingestion started. Data is being saved to the database in the background."
    }
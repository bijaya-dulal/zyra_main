# Inside your router:
from app.services.ingestion_service import IngestionService
from fastapi import APIRouter


router = APIRouter(prefix="", tags=["Documents"])

ingestion_service = IngestionService()

@router.post("/process/{doc_id}")
async def process_document(doc_id: str, file_path: str, subject: str):
    # This runs the whole pipeline you just built!
    processed_chunks = await ingestion_service.process_file(file_path, subject, doc_id)
    
    # Next step: Save processed_chunks to the database
    # (Using your search_service/db logic)
    return {"status": "success", "chunks_count": len(processed_chunks)}



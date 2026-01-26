from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from app.db import get_db
from app.services.rag_services import RAGService

router = APIRouter(tags=["RAG (AI Teacher)"])

# --- SCHEMAS ---
class QuestionRequest(BaseModel):
    query: str
    document_id: Optional[str] = None   # Optional: Limit context to one PDF
    subject_filter: Optional[str] = None 
    top_k: int = 5

class SourceItem(BaseModel):
    source_index: int
    chunk_id: str
    relevance_score: float

class QuestionResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    status: str
    query: str

# --- ENDPOINTS ---
@router.post("/ask", response_model=QuestionResponse)
async def ask_zyra(
    request: QuestionRequest, 
    db: AsyncSession = Depends(get_db)
):
    """
    Core RAG Endpoint:
    1. Receives student query.
    2. Retrieves relevant academic chunks.
    3. Generates answer using Gemini 2.5 Flash.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    service = RAGService(db)

    try:
        response = await service.answer_question(
            query=request.query,
            document_id=request.document_id,
            subject_filter=request.subject_filter,
            top_k=request.top_k
        )
        return response

    except Exception as e:
        # In production, log 'e' properly here
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while generating the answer: {str(e)}"
        )
    

    #update for the oauth 
    from fastapi import APIRouter, Depends
from app.routers.v1 import deps # Import the gatekeeper
from app.models.users import User
from app.schemas.user_schemas import UserOut

router = APIRouter()

@router.post("/ask")
async def ask_question(
    question: str, 
    # THIS LINE IS THE MAGIC:
    # It forces the user to be logged in. 
    # If they are, you get the 'current_user' object.
    current_user: User = Depends(deps.get_current_user) 
):
    print(f"User {current_user.email} (Role: {current_user.role}) is asking: {question}")
    
    # ... Your RAG Logic Here ...
    
    return {
        "answer": "This answer is protected. Only logged-in users see this.",
        "user": current_user.email
    }

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db import get_db
from app.services.exam_services import AsyncExamService
from app.schemas.exam_schemas import ExamCreate, ExamUpdate, ExamResponse

router = APIRouter(tags=["Exams"])

@router.get("/", response_model=List[ExamResponse])
async def list_exams(
    limit: int = Query(20, ge=1),
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    return await AsyncExamService.list_exams(db, limit, offset)

@router.post("/", response_model=ExamResponse, status_code=status.HTTP_201_CREATED)
async def create_exam(data: ExamCreate, db: AsyncSession = Depends(get_db)):
    return await AsyncExamService.create_exam(db, data)

@router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exam(exam_id: str, db: AsyncSession = Depends(get_db)):
    await AsyncExamService.delete_exam(db, exam_id)
    return None

@router.patch("/{exam_id}", response_model=ExamResponse)
async def update_exam(
    exam_id: str, 
    data: ExamUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Update exam details (e.g., change the starting_date for next year).
    """
    return await AsyncExamService.update_exam(db, exam_id, data)
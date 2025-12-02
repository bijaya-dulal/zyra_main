from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.schemas.exam_schemas import ExamCreate, ExamUpdate, ExamResponse
from app.services.exam_services import AsyncExamService


router = APIRouter(prefix="", tags=["Exams"])


@router.get("/", response_model=list[ExamResponse])
async def list_exams(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await AsyncExamService.list_exams(db, limit, offset)


@router.get("/{exam_id}", response_model=ExamResponse)
async def get_exam(
    exam_id: str,
    db: AsyncSession = Depends(get_db)
):
    return await AsyncExamService.get_exam(db, exam_id)


@router.post("/", response_model=ExamResponse, status_code=201)
async def create_exam(
    data: ExamCreate,
    db: AsyncSession = Depends(get_db)
):
    return await AsyncExamService.create_exam(db, data)


@router.put("/{exam_id}", response_model=ExamResponse)
async def update_exam(
    exam_id: str,
    data: ExamUpdate,
    db: AsyncSession = Depends(get_db)
):
    return await AsyncExamService.update_exam(db, exam_id, data)


@router.delete("/{exam_id}", status_code=204)
async def delete_exam(
    exam_id: str,
    db: AsyncSession = Depends(get_db)
):
    await AsyncExamService.delete_exam(db, exam_id)
    return None

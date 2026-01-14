from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db import get_db
from app.services.subject_service import AsyncSubjectService
from app.schemas.subject_schemas import SubjectCreate, SubjectUpdate, SubjectResponse

router = APIRouter(tags=["Subjects"])

@router.get("/", response_model=List[SubjectResponse])
async def list_subjects(
    limit: int = Query(20, ge=1),
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    return await AsyncSubjectService.list_subjects(db, limit, offset)

@router.post("/", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
async def create_subject(data: SubjectCreate, db: AsyncSession = Depends(get_db)):
    return await AsyncSubjectService.create_subject(db, data)

@router.patch("/{subject_id}", response_model=SubjectResponse)
async def update_subject(
    subject_id: str, 
    data: SubjectUpdate, 
    db: AsyncSession = Depends(get_db)
):
    return await AsyncSubjectService.update_subject(db, subject_id, data)

@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(subject_id: str, db: AsyncSession = Depends(get_db)):
    await AsyncSubjectService.delete_subject(db, subject_id)
    return None
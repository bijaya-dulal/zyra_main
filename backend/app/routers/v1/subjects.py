from fastapi import APIRouter, Depends, Query, status, Response
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.subject_schemas import (
    SubjectCreate,
    SubjectUpdate,
    SubjectResponse
)
from app.services.subject_service import AsyncSubjectService 


router = APIRouter(tags=["Subjects"])


# -----------------------
# LIST SUBJECTS
# -----------------------
@router.get("/", response_model=list[SubjectResponse])
async def list_subjects(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    subjects = await AsyncSubjectService.list_subjects(db, limit, offset)
    return subjects
# -----------------------
# GET SINGLE SUBJECT
# -----------------------
@router.get("/{subject_id}", response_model=SubjectResponse)
def get_subject(subject_id: str, db: Session = Depends(get_db)):
    return AsyncSubjectService.get_subject(db, subject_id)


# -----------------------
# CREATE SUBJECT
# -----------------------
@router.post(
    "/", 
    response_model=SubjectResponse, 
    status_code=status.HTTP_201_CREATED
)
def create_subject(data: SubjectCreate, db: Session = Depends(get_db)):
    return AsyncSubjectService.create_subject(db, data)


# -----------------------
# UPDATE SUBJECT
# -----------------------
@router.patch("/{subject_id}", response_model=SubjectResponse)
def update_subject(
    subject_id: str,
    data: SubjectUpdate,
    db: Session = Depends(get_db),
):
    return AsyncSubjectService.update_subject(db, subject_id, data)


# -----------------------
# DELETE SUBJECT
# -----------------------
@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(subject_id: str, db: Session = Depends(get_db)):
    AsyncSubjectService.delete_subject(db, subject_id)
    return




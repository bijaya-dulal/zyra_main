from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from uuid import uuid4

from app.models.exams import Exam
from app.schemas.exam_schemas import ExamCreate, ExamUpdate


class AsyncExamService:

    @staticmethod
    async def list_exams(db: AsyncSession, limit: int = 20, offset: int = 0):
        stmt = select(Exam).offset(offset).limit(limit)
        result = await db.scalars(stmt)
        return result.all()

    @staticmethod
    async def get_exam(db: AsyncSession, exam_id: str):
        stmt = select(Exam).where(Exam.id == exam_id)
        exam = await db.scalar(stmt)

        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam not found"
            )

        return exam

    @staticmethod
    async def create_exam(db: AsyncSession, data: ExamCreate):
        # 1. Check for duplicates (same Name + Board)
        # This prevents "Class 12 Science" from being created twice for "NEB"
        stmt = select(Exam).where(
            Exam.name == data.name, 
            Exam.board == data.board
        )
        existing_exam = await db.scalar(stmt)
        
        if existing_exam:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Exam '{data.name}' for board '{data.board}' already exists."
            )

        # 2. Create the Exam if it doesn't exist
        new_exam = Exam(
            id=str(uuid4()),
            **data.model_dump() # Automatically handles starting_date, description, etc.
        )

        db.add(new_exam)
        try:
            await db.commit()
            await db.refresh(new_exam)
            return new_exam
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def update_exam(db: AsyncSession, exam_id: str, data: ExamUpdate):
        # We reuse get_exam logic to handle 404 errors automatically
        exam = await AsyncExamService.get_exam(db, exam_id)

        # Dynamic update (date, name, description)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(exam, key, value)

        try:
            await db.commit()
            await db.refresh(exam)
            return exam
        except Exception as e:
            await db.rollback()
            # Catch duplicate errors if renaming an exam to one that already exists
            raise HTTPException(status_code=400, detail="Update failed. Check for duplicate exam names.")

    @staticmethod
    async def delete_exam(db: AsyncSession, exam_id: str):
        exam = await AsyncExamService.get_exam(db, exam_id)

        try:
            await db.delete(exam)
            await db.commit()
            return True
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
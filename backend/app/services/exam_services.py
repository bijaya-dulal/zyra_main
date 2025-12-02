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
        new_exam = Exam(
            id=str(uuid4()),
            **data.model_dump()
        )

        db.add(new_exam)
        await db.commit()
        await db.refresh(new_exam)
        return new_exam

    @staticmethod
    async def update_exam(db: AsyncSession, exam_id: str, data: ExamUpdate):
        exam = await AsyncExamService.get_exam(db, exam_id)

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(exam, key, value)

        await db.commit()
        await db.refresh(exam)
        return exam

    @staticmethod
    async def delete_exam(db: AsyncSession, exam_id: str):
        exam = await AsyncExamService.get_exam(db, exam_id)

        await db.delete(exam)
        await db.commit()
        return True

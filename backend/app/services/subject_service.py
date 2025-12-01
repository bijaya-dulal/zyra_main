from sqlalchemy.ext.asyncio import AsyncSession # Changed from synchronous Session
from sqlalchemy import select, delete # Needed for async queries
from fastapi import HTTPException, status
from uuid import uuid4

from app.models.subjects import Subject
from app.schemas.subject_schemas import SubjectCreate, SubjectUpdate


class AsyncSubjectService:
    """
    Handles all business logic and CRUD operations for the Subject model,
    using an asynchronous database session.
    """

    @staticmethod
    async def list_subjects(db: AsyncSession, limit: int = 20, offset: int = 0):
        # Build the SELECT statement
        stmt = select(Subject).offset(offset).limit(limit)
        # Execute the statement and return results
        result = await db.scalars(stmt)
        return result.all()

    @staticmethod
    async def get_subject(db: AsyncSession, subject_id: str):
        # Fetch the subject by ID asynchronously
        stmt = select(Subject).where(Subject.id == subject_id)
        subject = await db.scalar(stmt)
        
        # Raise 404 if not found
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found",
            )
        
        return subject

    @staticmethod
    async def create_subject(db: AsyncSession, data: SubjectCreate):
        # Create new model instance, including a new UUID
        new_subject = Subject(
            id=str(uuid4()),
            **data.model_dump() # Use model_dump() for Pydantic v2
        )
        
        # Add to session, commit, and refresh to get default values (like timestamps)
        db.add(new_subject)
        await db.commit()
        await db.refresh(new_subject)
        return new_subject

    @staticmethod
    async def update_subject(db: AsyncSession, subject_id: str, data: SubjectUpdate):
        # Fetch existing subject (reusing the get method)
        subject = await AsyncSubjectService.get_subject(db, subject_id)

        # Update model fields based on the Pydantic data
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(subject, key, value)

        # Commit changes and refresh
        await db.commit()
        await db.refresh(subject)
        return subject

    @staticmethod
    async def delete_subject(db: AsyncSession, subject_id: str):
        # Fetch existing subject
        subject = await AsyncSubjectService.get_subject(db, subject_id)
        
        # Delete and commit
        await db.delete(subject)
        await db.commit()
        return True
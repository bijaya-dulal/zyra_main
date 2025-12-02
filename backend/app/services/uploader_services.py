from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from uuid import uuid4

from app.models.uploaders import Uploader
from app.schemas.uploader_schemas import UploaderCreate, UploaderUpdate


class AsyncUploaderService:

    @staticmethod
    async def list_uploaders(db: AsyncSession, limit: int = 20, offset: int = 0):
        stmt = select(Uploader).offset(offset).limit(limit)
        result = await db.scalars(stmt)
        return result.all()

    @staticmethod
    async def get_uploader(db: AsyncSession, uploader_id: str):
        stmt = select(Uploader).where(Uploader.id == uploader_id)
        uploader = await db.scalar(stmt)

        if not uploader:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Uploader not found"
            )
        return uploader

    @staticmethod
    async def create_uploader(db: AsyncSession, data: UploaderCreate):
        uploader = Uploader(
            id=str(uuid4()),
            **data.model_dump()
        )
        db.add(uploader)
        await db.commit()
        await db.refresh(uploader)
        return uploader

    @staticmethod
    async def update_uploader(db: AsyncSession, uploader_id: str, data: UploaderUpdate):
        uploader = await AsyncUploaderService.get_uploader(db, uploader_id)

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(uploader, key, value)

        await db.commit()
        await db.refresh(uploader)
        return uploader

    @staticmethod
    async def delete_uploader(db: AsyncSession, uploader_id: str):
        uploader = await AsyncUploaderService.get_uploader(db, uploader_id)
        await db.delete(uploader)
        await db.commit()
        return True

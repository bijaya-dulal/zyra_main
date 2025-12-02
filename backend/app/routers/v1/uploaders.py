from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.services.uploader_services import AsyncUploaderService
from app.schemas.uploader_schemas import (
    UploaderCreate, UploaderUpdate, UploaderResponse
)

router = APIRouter(prefix="", tags=["Uploaders"])


@router.get("/", response_model=list[UploaderResponse])
async def list_uploaders(limit: int = 20, offset: int = 0, db: AsyncSession = Depends(get_db)):
    return await AsyncUploaderService.list_uploaders(db, limit, offset)


@router.get("/{uploader_id}", response_model=UploaderResponse)
async def get_uploader(uploader_id: str, db: AsyncSession = Depends(get_db)):
    return await AsyncUploaderService.get_uploader(db, uploader_id)


@router.post("/", response_model=UploaderResponse)
async def create_uploader(data: UploaderCreate, db: AsyncSession = Depends(get_db)):
    return await AsyncUploaderService.create_uploader(db, data)


@router.patch("/{uploader_id}", response_model=UploaderResponse)
async def update_uploader(uploader_id: str, data: UploaderUpdate, db: AsyncSession = Depends(get_db)):
    return await AsyncUploaderService.update_uploader(db, uploader_id, data)


@router.delete("/{uploader_id}")
async def delete_uploader(uploader_id: str, db: AsyncSession = Depends(get_db)):
    await AsyncUploaderService.delete_uploader(db, uploader_id)
    return {"message": "Uploader deleted successfully"}

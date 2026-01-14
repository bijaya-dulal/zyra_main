from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db import get_db
from app.services.uploader_services import AsyncUploaderService
from app.schemas.uploader_schemas import UploaderCreate, UploaderUpdate, UploaderResponse

router = APIRouter(tags=["Uploaders"])

@router.get("/", response_model=List[UploaderResponse])
async def list_uploaders(
    limit: int = 20, 
    offset: int = 0, 
    db: AsyncSession = Depends(get_db)
):
    return await AsyncUploaderService.list_uploaders(db, limit, offset)

@router.post("/", response_model=UploaderResponse, status_code=status.HTTP_201_CREATED)
async def create_uploader(data: UploaderCreate, db: AsyncSession = Depends(get_db)):
    return await AsyncUploaderService.create_uploader(db, data)
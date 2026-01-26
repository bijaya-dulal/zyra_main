from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db import get_db
from app.services.user_services import AsyncUserService
from app.schemas.user_schemas import UserCreate, UserUpdate, UserOut 

router = APIRouter(tags=["Users"])

@router.get("/", response_model=List[UserOut])
async def list_users(
    limit: int = 20, 
    offset: int = 0, 
    db: AsyncSession = Depends(get_db)
):
    return await AsyncUserService.list_users(db, limit, offset)

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await AsyncUserService.create_user(db, data)
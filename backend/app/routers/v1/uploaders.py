from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.services.uploader_services import AsyncUploaderService
from app.schemas.uploader_schemas import UploaderCreate, UploaderUpdate, UploaderResponse

# Use a specific prefix to avoid confusion during registration
router = APIRouter(tags=["Uploaders"])

@router.get("/", response_model=list[UploaderResponse])
async def list_uploaders(limit: int = 20, offset: int = 0, db: AsyncSession = Depends(get_db)):
    return await AsyncUploaderService.list_uploaders(db, limit, offset)

@router.post("/", response_model=UploaderResponse, status_code=status.HTTP_201_CREATED)
async def create_uploader(data: UploaderCreate, db: AsyncSession = Depends(get_db)):
    # Added error handling for production
    try:
        return await AsyncUploaderService.create_uploader(db, data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not create uploader: {str(e)}")

@router.patch("/{uploader_id}", response_model=UploaderResponse)
async def update_uploader(uploader_id: str, data: UploaderUpdate, db: AsyncSession = Depends(get_db)):
    updated = await AsyncUploaderService.update_uploader(db, uploader_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Uploader not found")
    return updated

@router.delete("/{uploader_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_uploader(uploader_id: str, db: AsyncSession = Depends(get_db)):
    success = await AsyncUploaderService.delete_uploader(db, uploader_id)
    if not success:
        raise HTTPException(status_code=404, detail="Uploader not found")
    return None
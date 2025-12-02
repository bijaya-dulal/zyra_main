from pydantic import BaseModel, EmailStr
from typing import Optional


class UploaderBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    user_type: Optional[str] = None
    phone: Optional[str] = None


class UploaderCreate(UploaderBase):
    pass


class UploaderUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    user_type: Optional[str] = None
    phone: Optional[str] = None


class UploaderResponse(UploaderBase):
    id: str

    class Config:
        from_attributes = True

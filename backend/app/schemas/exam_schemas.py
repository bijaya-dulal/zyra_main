from pydantic import BaseModel
from datetime import date
from typing import Optional


class ExamBase(BaseModel):
    name: str
    board: str
    starting_date: Optional[date] = None
    description: Optional[str] = None


class ExamCreate(ExamBase):
    pass


class ExamUpdate(BaseModel):
    name: Optional[str] = None
    board: Optional[str] = None
    starting_date: Optional[date] = None
    description: Optional[str] = None


class ExamResponse(ExamBase):
    id: str

    class Config:
        from_attributes = True  # needed for ORM

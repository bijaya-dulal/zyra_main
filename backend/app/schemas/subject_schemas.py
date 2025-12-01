from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


# -----------------------
# Base Schema
# -----------------------
class SubjectBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    class_name: str = Field(..., min_length=1)
    course_name: str = Field(..., min_length=2)
    description: Optional[str] = None
    full_mark: Optional[int] = Field(None, ge=0)
    pass_mark: Optional[int] = Field(None, ge=0)
    theory_mark: Optional[int] = Field(None, ge=0)
    practical_mark: Optional[int] = Field(None, ge=0)
    exam_id: str


# -----------------------
# Create Schema
# -----------------------
class SubjectCreate(SubjectBase):
    pass


# -----------------------
# Update Schema
# -----------------------
class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    class_name: Optional[str] = None
    course_name: Optional[str] = None
    description: Optional[str] = None
    full_mark: Optional[int] = Field(None, ge=0)
    pass_mark: Optional[int] = Field(None, ge=0)
    theory_mark: Optional[int] = Field(None, ge=0)
    practical_mark: Optional[int] = Field(None, ge=0)


# -----------------------
# Response Schema
# -----------------------
class SubjectResponse(SubjectBase):
    id: str

    class Config:
        orm_mode = True

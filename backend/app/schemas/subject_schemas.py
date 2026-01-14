from pydantic import BaseModel
from typing import Optional

# Base Schema (Shared properties)
class SubjectBase(BaseModel):
    name: str
    grade_name: str            # ✅ FIXED: Was likely 'class_name' before
    course_name: str
    description: Optional[str] = None
    
    full_mark: Optional[int] = 100
    pass_mark: Optional[int] = 40
    theory_mark: Optional[int] = 75
    practical_mark: Optional[int] = 25

# Schema for CREATING a subject
class SubjectCreate(SubjectBase):
    # id: Optional[str] = None
    
    # ✅ FIXED: Made Optional to match DB 'nullable=True'
    # This allows you to create a Subject without an Exam first
    exam_id: Optional[str] = None 

# Schema for UPDATING
class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    grade_name: Optional[str] = None
    course_name: Optional[str] = None
    description: Optional[str] = None
    exam_id: Optional[str] = None

# Schema for READING (Response)
class SubjectResponse(SubjectBase):
    id: str
    exam_id: Optional[str] = None

    class Config:
        from_attributes = True
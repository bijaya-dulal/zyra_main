from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(String, primary_key=True, index=True)

    # Main subject info
    name = Column(String(100), nullable=False)
    class_name = Column(String(50), nullable=False)

    course_name = Column(String(150), unique=True, nullable=False, index=True)  
    description = Column(Text)

    full_mark = Column(Integer)
    pass_mark = Column(Integer)
    theory_mark = Column(Integer)
    practical_mark = Column(Integer)

    # Foreign Key to Exams table
    exam_id = Column(String, ForeignKey("exams.id"), nullable=False)

    # Relationships
    exam = relationship("Exam", back_populates="subjects")
    documents = relationship("Document", back_populates="subject", cascade="all, delete")  

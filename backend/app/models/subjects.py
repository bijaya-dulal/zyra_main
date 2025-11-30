from sqlalchemy import Column, String, Integer, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db import Base

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(String, primary_key=True, index=True)

    name = Column(String(100), nullable=False)
    grade_name = Column(String(50), nullable=False)
    course_name = Column(String(150), nullable=False, index=True)
    description = Column(Text)

    full_mark = Column(Integer)
    pass_mark = Column(Integer)
    theory_mark = Column(Integer)
    practical_mark = Column(Integer)

    exam_id = Column(String, ForeignKey("exams.id"), nullable=True)

    exam = relationship("Exam", back_populates="subjects")
    documents = relationship("Document", back_populates="subject", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('name', 'grade_name', 'exam_id'),
    )

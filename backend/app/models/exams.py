from sqlalchemy import Column, String, Text, Date ,UniqueConstraint
from sqlalchemy.orm import relationship
from app.db import Base


class Exam(Base):
    __tablename__ = "exams"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    board = Column(String, nullable=False)
    starting_date = Column(Date, nullable=True)
    description = Column(Text, nullable=True)

    # 🔥 One exam has many subjects
    subjects = relationship(
        "Subject",
        back_populates="exam",
        cascade="all"  # Keep 'all' for saving/deleting related subjects in a session, but remove 'delete-orphan'
)

# ✅ CONSTRAINT:
    # Prevents duplicate categories. 
    # You cannot have two "Class 12 Science" entries for "NEB".
    __table_args__ = (
        UniqueConstraint('name', 'board', name='uq_exam_category'),
    )
    
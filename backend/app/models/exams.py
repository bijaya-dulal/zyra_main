from sqlalchemy import Column, String, Text, Date
from sqlalchemy.orm import relationship
from app.db import Base


class Exam(Base):
    __tablename__ = "exams"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    board = Column(String, nullable=False)
    starting_date = Column(Date)
    description = Column(Text, nullable=True)

    # 🔥 One exam has many subjects
    subjects = relationship(
        "Subject",
        back_populates="exam",
        cascade="all, delete-orphan"  # deleting exam deletes all subjects
    )
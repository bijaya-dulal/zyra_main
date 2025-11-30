from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.db import Base


class Uploader(Base):
    __tablename__ = "uploaders"

    id = Column(String, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=True)
    user_type = Column(String(20))  # admin / teacher / student
    phone = Column(String(20), nullable=True)

    documents = relationship(
        "Document",
        back_populates="uploader",
        passive_deletes=True
    )

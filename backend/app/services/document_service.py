from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from uuid import uuid4

from app.models.documents import Document
from app.schemas.document_schemas import DocumentCreate, DocumentUpdate


class AsyncDocumentService:
    """
    Handles CRUD operations for the Document model using async SQLAlchemy.
    """

    # LIST DOCUMENTS WITH OPTIONAL FILTERS
    @staticmethod
    async def list_documents(
        db: AsyncSession,
        subject_id: str | None = None,
        doc_type: str | None = None,
        status: str | None = None,
        language: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ):
        stmt = select(Document)

        if subject_id:
            stmt = stmt.where(Document.subject_id == subject_id)
        if doc_type:
            stmt = stmt.where(Document.doc_type == doc_type)
        if status:
            stmt = stmt.where(Document.status == status)
        if language:
            stmt = stmt.where(Document.language == language)

        stmt = stmt.offset(offset).limit(limit).order_by(Document.created_at.desc())

        result = await db.scalars(stmt)
        return result.all()

    # GET ONE DOCUMENT
    @staticmethod
    async def get_document(db: AsyncSession, doc_id: str):
        stmt = select(Document).where(Document.id == doc_id)
        document = await db.scalar(stmt)

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )
        return document

    # CREATE DOCUMENT
    @staticmethod
    async def create_document(db: AsyncSession, data: DocumentCreate):
        new_doc = Document(
            id=str(uuid4()),
            **data.model_dump()  # Pydantic v2
        )

        db.add(new_doc)
        await db.commit()
        await db.refresh(new_doc)
        return new_doc

    # UPDATE DOCUMENT
    @staticmethod
    async def update_document(db: AsyncSession, doc_id: str, data: DocumentUpdate):
        document = await AsyncDocumentService.get_document(db, doc_id)

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(document, key, value)

        await db.commit()
        await db.refresh(document)
        return document

    # DELETE DOCUMENT
    @staticmethod
    async def delete_document(db: AsyncSession, doc_id: str):
        document = await AsyncDocumentService.get_document(db, doc_id)

        await db.delete(document)
        await db.commit()
        return True

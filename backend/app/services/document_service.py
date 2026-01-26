import uuid
import logging
from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import HTTPException

from app.models.documents import Document
from app.models.chunks import Chunk
from app.models.embeddings import Embedding
from app.schemas.document_schemas import DocumentCreate, DocumentUpdate
from app.services.ingestion_service import IngestionService
from app.models.users import User # Make sure to import this!

logger = logging.getLogger(__name__)

class AsyncDocumentService:
    """
    Production-level service for Document lifecycle.
    Handles Metadata CRUD + High-Performance RAG Ingestion.
    """

    # ==========================================
    # 1. MISSING CRUD METHODS (ADD THESE)
    # ==========================================

    @staticmethod
    async def create_document(db: AsyncSession, data: DocumentCreate) -> Document:
        """Creates a new document metadata record."""
        # --- NEW LOGIC START ---
        # If the user didn't send an uploader_id, find the first Admin automatically
        final_uploader_id = data.uploader_id
        
        if not final_uploader_id:
            # SQL: SELECT id FROM uploaders WHERE user_type = 'admin' LIMIT 1
            stmt = select(User.id).where(User.user_type == "admin").limit(1)
            result = await db.execute(stmt)
            admin_id = result.scalar_one_or_none()
            
            if admin_id:
                final_uploader_id = admin_id
            else:
                # Fallback: If no admin exists, we can't save it (or you could raise an error)
                # For now, let's assume you created the admin in the previous step.
                raise HTTPException(status_code=400, detail="No Uploader ID provided and no Admin found in DB.")
        # --- NEW LOGIC END ---

        # Generate a UUID if not provided (though your model might handle it)
        new_doc_id = str(uuid.uuid4())
        

        new_doc = Document(
            id=new_doc_id,
            title=data.title,
            description=data.description,
            doc_type=data.doc_type,
            uri=data.uri,
            language=data.language,
            subject_id=data.subject_id,
            uploader_id=data.uploader_id,
            status="pending" # Default status before processing
        )
        
        db.add(new_doc)
        await db.commit()
        await db.refresh(new_doc)
        return new_doc

    @staticmethod
    async def update_document(db: AsyncSession, doc_id: str, data: DocumentUpdate) -> Optional[Document]:
        """Updates an existing document."""
        doc = await AsyncDocumentService.get_document(db, doc_id)
        if not doc:
            return None
        
        # Update fields if they are provided in the request
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(doc, key, value)
            
        await db.commit()
        await db.refresh(doc)
        return doc

    @staticmethod
    async def delete_document(db: AsyncSession, doc_id: str) -> bool:
        """Deletes a document and relies on Cascade to remove chunks."""
        doc = await AsyncDocumentService.get_document(db, doc_id)
        if not doc:
            return False
            
        await db.delete(doc)
        await db.commit()
        return True

    # ==========================================
    # 2. EXISTING READ METHODS
    # ==========================================

    @staticmethod
    async def list_documents(
        db: AsyncSession,
        subject_id: Optional[str] = None,
        doc_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ):
        stmt = select(Document)
        if subject_id:
            stmt = stmt.where(Document.subject_id == subject_id)
        if doc_type:
            stmt = stmt.where(Document.doc_type == doc_type)
        
        stmt = stmt.offset(offset).limit(limit).order_by(Document.created_at.desc())
        result = await db.execute(stmt) # Fixed: use db.execute for async
        return result.scalars().all()

    @staticmethod
    async def get_document(db: AsyncSession, doc_id: str):
        result = await db.execute(select(Document).where(Document.id == doc_id))
        return result.scalar_one_or_none()

    # ==========================================
    # 3. RAG PERSISTENCE & INGESTION
    # ==========================================

    @staticmethod
    async def save_rag_content(
        db: AsyncSession, 
        document_id: str, 
        processed_chunks: List[Any]
    ) -> bool:
        """
        ATOMIC OPERATION: Saves Chunks and Embeddings.
        """
        try:
            for i, p_chunk in enumerate(processed_chunks):
                chunk_uuid = str(uuid.uuid4())

                # 1. Prepare Chunk Record
                new_chunk = Chunk(
                    id=chunk_uuid,
                    document_id=document_id,
                    chunk_index=i,
                    content=p_chunk.content,
                    token_count=getattr(p_chunk, 'token_count', 0),
                    chunk_type=getattr(p_chunk, 'chunk_type', 'text'),
                    start_index=getattr(p_chunk, 'start_index', 0),
                    end_index=getattr(p_chunk, 'end_index', 0),
                    # Ensure column name matches model ('meta_data')
                    meta_data=getattr(p_chunk, 'chunk_metadata', {})
                )
                db.add(new_chunk)

                # 2. Prepare Embedding Record
                if hasattr(p_chunk, 'vector') and p_chunk.vector:
                    new_emb = Embedding(
                        id=str(uuid.uuid4()),
                        chunk_id=chunk_uuid,
                        embedding_vector=p_chunk.vector,
                        model_name="all-mpnet-base-v2"
                    )
                    db.add(new_emb)

            await db.flush() 
            return True

        except Exception as e:
            logger.error(f"Persistence Error: {e}")
            raise HTTPException(
                status_code=500, 
                detail="Database error during chunk persistence."
            )

    @staticmethod
    async def process_and_finalize(
        db: AsyncSession, 
        file_path: str, 
        subject_name: str, 
        document_id: str
    ):
        """
        Background Task: Orchestrator
        """
        logger.info(f"Starting finalization for document {document_id}")
        ingestion_service = IngestionService()
        
        try:
            # 1. Logic: Extract & Embed
            processed_chunks = await ingestion_service.process_file(
                file_path=file_path,
                subject=subject_name,
                document_id=document_id
            )

            # 2. Persistence: Save to DB
            await AsyncDocumentService.save_rag_content(
                db=db,
                document_id=document_id,
                processed_chunks=processed_chunks
            )

            # 3. Status Update: Complete
            doc = await AsyncDocumentService.get_document(db, document_id)
            if doc:
                doc.status = "completed"
                await db.commit()
            
            logger.info(f"Document {document_id} fully processed.")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Pipeline failed for {document_id}: {e}")
            doc = await AsyncDocumentService.get_document(db, document_id)
            if doc:
                doc.status = "error"
                await db.commit()
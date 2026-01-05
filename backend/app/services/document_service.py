#############################################################
# backend/app/services/document_service.py  
# Production-level service for Document lifecycle.
# Handles Metadata CRUD + High-Performance RAG Ingestion.   
# helps to manage documents and their associated chunks and embeddings. 
# And saves them to the database.
############################################



#############################################################
# Standard Library Imports
#############################################################

import uuid
import logging
from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import HTTPException, status
from fastapi.concurrency import run_in_threadpool
#############################################################
# Import application-specific modules and models
#############################################################       

from app.models.documents import Document
from app.models.chunks import Chunk
from app.models.embeddings import Embedding
from app.schemas.document_schemas import DocumentCreate, DocumentUpdate
from app.services.extractor.pipeline import ExtractionPipeline
from app.services.ingestion_service import IngestionService

logger = logging.getLogger(__name__)

class AsyncDocumentService:
    """
    Production-level service for Document lifecycle.
    Handles Metadata CRUD + High-Performance RAG Ingestion.
    """

    # --- STANDARD CRUD SECTION ---

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
        result = await db.scalars(stmt)
        return result.all()

    @staticmethod
    async def get_document(db: AsyncSession, doc_id: str):
        stmt = select(Document).where(Document.id == doc_id)
        document = await db.scalar(stmt)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document

    # --- PRODUCTION RAG PERSISTENCE SECTION ---

    @staticmethod
    async def save_rag_content(
        db: AsyncSession, 
        document_id: str, 
        processed_chunks: List[Any]
    ) -> bool:
        """
        ATOMIC OPERATION: Saves Chunks and Embeddings.
        In production, we use db.begin() or flushes to ensure data integrity.
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
                    metadata=getattr(p_chunk, 'chunk_metadata', {})
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
            logger.info(f"Buffered {len(processed_chunks)} chunks for doc {document_id}")
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
        The Orchestrator for the background task.
        Connects the IngestionService (Logic) to the Database (Persistence).
        """
        logger.info(f"Starting finalization for document {document_id}")
        
        # 1. Initialize Ingestion Logic
        ingestion_service = IngestionService()
        
        try:
            # 2. Extract, Chunk, and Embed (Heavy ML Tasks)
            processed_chunks = await ingestion_service.process_file(
                file_path=file_path,
                subject=subject_name,
                document_id=document_id
            )

            # 3. Persist results to DB
            await AsyncDocumentService.save_rag_content(
                db=db,
                document_id=document_id,
                processed_chunks=processed_chunks
            )

            # 4. Update Document Status to 'completed'
            doc = await AsyncDocumentService.get_document(db, document_id)
            doc.status = "completed"
            
            await db.commit()
            logger.info(f"Document {document_id} fully processed and finalized.")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Pipeline failed for {document_id}: {e}")
            # Update status to failed
            try:
                doc = await AsyncDocumentService.get_document(db, document_id)
                doc.status = "error"
                await db.commit()
            except:
                pass
            raise e
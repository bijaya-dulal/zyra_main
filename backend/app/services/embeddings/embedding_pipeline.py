
# ============================================================================
# File: app/services/embedding/embedding_pipeline.py
# Pipeline: Extract → Chunk → Embed → Save
# Integrates with your existing chunking system
# ============================================================================
from sqlalchemy.orm import Session
from app.models.chunks import Chunk
from app.models.embeddings import Embedding
from app.services.embeddings.embeding_services import EmbeddingService
from typing import List, Optional
import uuid
import logging

logger = logging.getLogger(__name__)


class EmbeddingPipeline:
    """
    Complete pipeline integrating with your existing chunking system:
    
    Your Flow:
    1. Extract text (ExtractionPipeline) ✓ You have this
    2. Chunk text (AcademicChunker) ✓ You have this
    3. Convert to DB (ChunkAdapter) ✓ You have this
    4. Generate embeddings ← This pipeline handles this
    5. Save to database ← This pipeline handles this
    """
    
    def __init__(
        self, 
        db: Session,
        model_name: str = 'all-mpnet-base-v2'
    ):
        """
        Initialize embedding pipeline.
        
        Args:
            db: SQLAlchemy database session
            model_name: Embedding model to use
        """
        self.db = db
        self.embedding_service = EmbeddingService(model_name=model_name)
        self.model_name = model_name
        self.dimensions = self.embedding_service.dimensions
        logger.info(f"Embedding pipeline ready: {model_name} ({self.dimensions}d)")
    
    def process_chunk(self, chunk: Chunk) -> Embedding:
        """
        Process single chunk: generate embedding and save.
        
        Args:
            chunk: Chunk object from database (created by ChunkAdapter)
            
        Returns:
            Created Embedding object
        """
        try:
            # Check if embedding already exists
            existing = self.db.query(Embedding).filter(
                Embedding.chunk_id == chunk.id
            ).first()
            
            if existing:
                logger.debug(f"Embedding exists for chunk {chunk.id}")
                return existing
            
            # Generate embedding
            logger.debug(f"Generating embedding for chunk {chunk.id}")
            embedding_vector = self.embedding_service.embed_single(
                chunk.content,
                normalize=True
            )
            
            # Create embedding record
            embedding = Embedding(
                id=str(uuid.uuid4()),
                chunk_id=chunk.id,
                embedding_vector=embedding_vector.tolist(),  # Convert to list for PostgreSQL
                model_name=self.model_name,
                dimensions=self.dimensions
            )
            
            # Save to database
            self.db.add(embedding)
            self.db.commit()
            self.db.refresh(embedding)
            
            logger.info(f"✓ Created embedding for chunk {chunk.id}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error processing chunk {chunk.id}: {e}")
            self.db.rollback()
            raise
    
    def process_chunks_batch(
        self,
        chunks: List[Chunk],
        batch_size: int = 32,
        skip_existing: bool = True
    ) -> List[Embedding]:
        """
        Process multiple chunks efficiently (RECOMMENDED for bulk processing).
        
        Args:
            chunks: List of Chunk objects from database
            batch_size: Number of chunks to process at once
            skip_existing: Skip chunks that already have embeddings
            
        Returns:
            List of created Embedding objects
        """
        if not chunks:
            return []
        
        logger.info(f"Processing {len(chunks)} chunks (batch_size={batch_size})")
        
        try:
            # Filter out existing embeddings
            if skip_existing:
                existing_ids = set(
                    e.chunk_id for e in 
                    self.db.query(Embedding.chunk_id).filter(
                        Embedding.chunk_id.in_([c.id for c in chunks])
                    ).all()
                )
                chunks_to_process = [c for c in chunks if c.id not in existing_ids]
                logger.info(
                    f"Skipping {len(existing_ids)} existing. "
                    f"Processing {len(chunks_to_process)} new."
                )
            else:
                chunks_to_process = chunks
            
            if not chunks_to_process:
                logger.info("All chunks already have embeddings")
                return []
            
            # Extract texts
            texts = [chunk.content for chunk in chunks_to_process]
            
            # Generate embeddings in batch (efficient!)
            logger.info("Generating embeddings...")
            embedding_vectors = self.embedding_service.embed_batch(
                texts,
                batch_size=batch_size,
                normalize=True,
                show_progress=True
            )
            
            # Create embedding records
            logger.info("Saving to database...")
            embeddings = []
            
            for chunk, embedding_vector in zip(chunks_to_process, embedding_vectors):
                embedding = Embedding(
                    id=str(uuid.uuid4()),
                    chunk_id=chunk.id,
                    embedding_vector=embedding_vector.tolist(),
                    model_name=self.model_name,
                    dimensions=self.dimensions
                )
                embeddings.append(embedding)
            
            # Bulk insert (fast!)
            self.db.bulk_save_objects(embeddings)
            self.db.commit()
            
            logger.info(f"✓ Created {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error processing batch: {e}")
            self.db.rollback()
            raise
    
    def process_document(
        self,
        document_id: str,
        batch_size: int = 32
    ) -> List[Embedding]:
        """
        Process all chunks for a document.
        
        This is what you'll use after chunking a document!
        
        Your workflow:
        1. Extract PDF → text
        2. Chunk text → ProcessingChunks
        3. Convert to DB → DBChunks (saved to database)
        4. Call this method → Embeddings created!
        
        Args:
            document_id: Document ID
            batch_size: Batch size for processing
            
        Returns:
            List of created Embedding objects
        """
        logger.info(f"Processing embeddings for document {document_id}")
        
        # Get all chunks for this document
        chunks = self.db.query(Chunk).filter(
            Chunk.document_id == document_id
        ).order_by(Chunk.chunk_index).all()
        
        if not chunks:
            logger.warning(f"No chunks found for document {document_id}")
            return []
        
        logger.info(f"Found {len(chunks)} chunks")
        
        # Process in batch
        return self.process_chunks_batch(
            chunks,
            batch_size=batch_size,
            skip_existing=True
        )
    
    def get_embedding_stats(self, document_id: str) -> dict:
        """
        Get embedding statistics for a document.
        
        Returns:
            Dict with stats: total_chunks, embedded_chunks, missing, percentage
        """
        total_chunks = self.db.query(Chunk).filter(
            Chunk.document_id == document_id
        ).count()
        
        embedded_chunks = self.db.query(Embedding).join(
            Chunk, Embedding.chunk_id == Chunk.id
        ).filter(
            Chunk.document_id == document_id
        ).count()
        
        return {
            "document_id": document_id,
            "total_chunks": total_chunks,
            "embedded_chunks": embedded_chunks,
            "missing_embeddings": total_chunks - embedded_chunks,
            "completion_percentage": (embedded_chunks / total_chunks * 100) if total_chunks > 0 else 0
        }

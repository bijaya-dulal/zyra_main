import logging
from typing import List, Dict, Any
from app.services.extractor.pipeline import ExtractionPipeline
from app.services.chunk_services.chunker import AcademicChunker
from app.services.embeddings.embeding_services import EmbeddingService
from app.schemas.chunk_schemas import ChunkBase

logger = logging.getLogger(__name__)

class IngestionService:
    """
    Orchestrates the full document processing flow:
    Extraction -> Chunking -> Embedding
    """

    def __init__(self):
        self.extractor = ExtractionPipeline()
        self.chunker = AcademicChunker(max_chunk_size=1000, overlap=200)
        self.embedding_service = EmbeddingService()

    async def process_file(self, file_path: str, subject: str, document_id: str) -> List[ChunkBase]:
        """
        Takes a local file path and returns a list of chunks with embeddings.
        """
        logger.info(f"Starting ingestion for: {file_path}")

        # 1. Extraction
        # Returns: {"raw_text": str, "markdown": str, "meta": dict}
        extraction_result = await self.extractor.extract(file_path, subject)
        content = extraction_result.get("markdown") or extraction_result.get("raw_text")

        if not content:
            logger.error("Extraction returned empty content.")
            return []

        # 2. Chunking
        # Returns a list of Chunk objects (schemas/chunk.py)
        document_metadata = {
            "document_id": document_id,
            "subject": subject,
            "source": file_path
        }
        chunks = self.chunker.chunk_document(content, metadata=document_metadata)

        if not chunks:
            logger.warning("No chunks created from content.")
            return []

        # 3. Embedding (Batch processing for efficiency)
        texts_to_embed = [c.content for c in chunks]
        embeddings = self.embedding_service.embed_batch(texts_to_embed)

        # 4. Attach embeddings to Chunk objects
        for i, chunk in enumerate(chunks):
            # Convert numpy array to list for JSON/Database compatibility
            chunk.vector = embeddings[i].tolist()

        logger.info(f"Successfully processed {len(chunks)} chunks for document {document_id}")
        return chunks
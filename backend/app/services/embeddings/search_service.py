from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.chunks import Chunk
from app.models.embeddings import Embedding
from app.services.exam_services import EmbeddingService
from typing import List, Tuple, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self, db: AsyncSession, embedding_service: EmbeddingService):
        self.db = db
        self.embedding_service = embedding_service

    async def search(
        self,
        query: str,
        top_k: int = 5,
        document_id: Optional[str] = None
    ) -> List[Tuple[Chunk, float]]:
        """
        Asynchronously searches for similar chunks.
        """
        # 1. Generate query embedding
        query_vec = self.embedding_service.embed_single(query)

        # 2. Fetch embeddings from DB (Async way)
        stmt = select(Embedding, Chunk).join(Chunk, Embedding.chunk_id == Chunk.id)
        if document_id:
            stmt = stmt.where(Chunk.document_id == document_id)
        
        result = await self.db.execute(stmt)
        rows = result.all() # List of (Embedding, Chunk)

        if not rows:
            return []

        # 3. Calculate similarities
        scored_results = []
        for emb_obj, chunk_obj in rows:
            # Assumes emb_obj.embedding_vector is a list/array stored in DB
            chunk_vec = np.array(emb_obj.embedding_vector)
            sim = self.embedding_service.compute_similarity(query_vec, chunk_vec)
            scored_results.append((chunk_obj, sim))

        # 4. Sort and return
        scored_results.sort(key=lambda x: x[1], reverse=True)
        return scored_results[:top_k]
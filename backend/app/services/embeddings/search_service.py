from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.chunks import Chunk
from app.models.embeddings import Embedding # Ensure this matches your file structure
from app.services.embeddings.embeding_services import EmbeddingService # Fixed import path
from typing import List, Tuple, Optional
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
        Asynchronously searches for similar chunks using pgvector in the database.
        """
        # 1. Generate query embedding (CPU-only via EmbeddingService)
        query_vec = self.embedding_service.embed_single(query)

        # 2. Construct pgvector Query
        # We calculate 'distance' (lower is better).
        # We select the Chunk and the calculated distance.
        distance_expr = Embedding.embedding_vector.cosine_distance(query_vec)
        
        stmt = select(Chunk, distance_expr.label("distance")) \
            .join(Embedding, Embedding.chunk_id == Chunk.id)

        # 3. Apply Filters
        if document_id:
            stmt = stmt.where(Chunk.document_id == document_id)

        # 4. Order by distance (Ascending = closest match first) and Limit
        stmt = stmt.order_by(distance_expr).limit(top_k)

        # 5. Execute
        result = await self.db.execute(stmt)
        rows = result.all() # Returns List of (Chunk, distance)

        # 6. Convert Distance to Similarity Score
        # Cosine Similarity = 1 - Cosine Distance
        # pgvector returns distance, so we flip it for the RAG prompt ranking
        scored_results = []
        for chunk, distance in rows:
            similarity = 1 - distance
            scored_results.append((chunk, similarity))

        return scored_results
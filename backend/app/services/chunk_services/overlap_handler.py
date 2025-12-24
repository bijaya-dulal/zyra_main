# ============================================================================
# File: app/services/chunking/overlap_handler.py
# Adds overlap between chunks
# ============================================================================
import logging
from typing import List
from app.models.chunks import Chunk
from app.utils.text_splitter import rough_token_count

logger = logging.getLogger(__name__)


class OverlapHandler:
    """Handles adding overlap context between adjacent chunks."""
    
    def __init__(self, overlap_size: int):
        self.overlap_size = overlap_size
    
    def add_overlap(self, chunks: List[Chunk]) -> List[Chunk]:
        """
        Add overlapping context from adjacent chunks.
        
        This helps with:
        - Queries that span chunk boundaries
        - Maintaining context for better embeddings
        """
        if len(chunks) <= 1 or self.overlap_size == 0:
            return chunks

        result = []
        
        try:
            for i, chunk in enumerate(chunks):
                content = chunk.content
                metadata = chunk.metadata.copy()

                # Add previous overlap
                if i > 0:
                    prev_chunk = chunks[i - 1]
                    overlap_text = self._extract_overlap(
                        prev_chunk.content, # type: ignore
                        from_end=True
                    )
                    if overlap_text:
                        content = f"[...{overlap_text}] {content}"
                        metadata['has_previous_overlap'] = True

                # Add next overlap
                if i < len(chunks) - 1:
                    next_chunk = chunks[i + 1]
                    overlap_text = self._extract_overlap(
                        next_chunk.content, # type: ignore
                        from_end=False
                    )
                    if overlap_text:
                        content = f"{content} [{overlap_text}...]"
                        metadata['has_next_overlap'] = True

                # Create updated chunk
                result.append(Chunk(
                    content=content,
                    chunk_type=chunk.chunk_type,
                    metadata=metadata,
                    start_index=chunk.start_index,
                    end_index=chunk.end_index,
                    token_count=rough_token_count(content) # type: ignore
                ))

            return result
        
        except Exception as e:
            logger.error(f"Error adding overlap: {e}")
            return chunks
    
    def _extract_overlap(self, text: str, from_end: bool) -> str:
        """Extract overlap text, respecting sentence boundaries."""
        overlap_chars = self.overlap_size * 4
        
        if from_end:
            overlap = text[-overlap_chars:]
            # Find last period for clean boundary
            last_period = overlap.rfind('.')
            if last_period > len(overlap) // 2:
                overlap = overlap[last_period + 1:].strip()
        else:
            overlap = text[:overlap_chars]
            # Find first period for clean boundary
            first_period = overlap.find('.')
            if 0 < first_period < len(overlap) // 2:
                overlap = overlap[:first_period + 1].strip()
        
        return overlap
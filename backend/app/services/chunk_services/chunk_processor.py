# Processes sections into chunks
# ============================================================================
import logging
from typing import List, Dict
from app.models.chunks import Chunk
from app.utils.text_splitter import rough_token_count, split_sentences

logger = logging.getLogger(__name__)


class ChunkProcessor:
    """Processes sections into appropriately sized chunks."""
    
    def __init__(self, max_chunk_size: int, min_chunk_size: int):
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
    
    def process_section(
        self,
        section: Dict,
        base_metadata: Dict
    ) -> List[Chunk]:
        """
        Chunk a single section, respecting max size.
        
        Returns:
            List of Chunk objects
        """
        try:
            content = section['content']
            section_type = section['type']
            
            # Count tokens safely
            try:
                token_count = rough_token_count(content)
            except TypeError as e:
                logger.error(f"Token counting failed: {e}")
                token_count = len(content) // 4

            # If small enough, return as single chunk
            if token_count <= self.max_chunk_size:
                return [self._create_chunk(
                    content=content,
                    section_type=section_type,
                    metadata=base_metadata,
                    start=section['start'],
                    end=section['end'],
                    token_count=token_count
                )]

            # Split large section
            return self._split_large_section(section, base_metadata)
        
        except Exception as e:
            logger.error(f"Error processing section: {e}")
            # Return section as-is if processing fails
            return [self._create_chunk(
                content=section['content'],
                section_type=section['type'],
                metadata={**base_metadata, 'error': 'processing_failed'},
                start=section.get('start', 0),
                end=section.get('end', len(section['content'])),
                token_count=rough_token_count(section['content'])
            )]
    
    def _split_large_section(
        self,
        section: Dict,
        base_metadata: Dict
    ) -> List[Chunk]:
        """Split large section into smaller chunks by sentences."""
        try:
            sentences = split_sentences(section['content'])
            
            if not sentences:
                logger.warning("No sentences found, returning as single chunk")
                return [self._create_chunk(
                    content=section['content'],
                    section_type=section['type'],
                    metadata=base_metadata,
                    start=section['start'],
                    end=section['end'],
                    token_count=rough_token_count(section['content'])
                )]
            
            chunks = []
            sentence_buffer = []
            buffer_size = 0
            chunk_start = section['start']

            for sentence in sentences:
                sentence_size = rough_token_count(sentence)
                
                if buffer_size + sentence_size > self.max_chunk_size and sentence_buffer:
                    # Create chunk
                    chunk_text = " ".join(sentence_buffer)
                    chunk_end = chunk_start + len(chunk_text)
                    
                    chunks.append(self._create_chunk(
                        content=chunk_text,
                        section_type=section['type'],
                        metadata=base_metadata,
                        start=chunk_start,
                        end=chunk_end,
                        token_count=buffer_size
                    ))
                    
                    # Reset buffer
                    sentence_buffer = [sentence]
                    buffer_size = sentence_size
                    chunk_start = chunk_end
                else:
                    sentence_buffer.append(sentence)
                    buffer_size += sentence_size

            # Add remaining sentences
            if sentence_buffer:
                chunk_text = " ".join(sentence_buffer)
                chunks.append(self._create_chunk(
                    content=chunk_text,
                    section_type=section['type'],
                    metadata=base_metadata,
                    start=chunk_start,
                    end=section['end'],
                    token_count=buffer_size
                ))

            return chunks
        
        except Exception as e:
            logger.error(f"Error splitting large section: {e}")
            # Fallback
            return [self._create_chunk(
                content=section['content'],
                section_type=section['type'],
                metadata={**base_metadata, 'error': 'split_failed'},
                start=section.get('start', 0),
                end=section.get('end', len(section['content'])),
                token_count=rough_token_count(section['content'])
            )]
    
    def _create_chunk(
        self,
        content: str,
        section_type,
        metadata: Dict,
        start: int,
        end: int,
        token_count: int
    ) -> Chunk:
        """Helper to create a Chunk object."""
        return Chunk(
            content=content,
            chunk_type=section_type,
            metadata={**metadata, 'section_type': section_type.value},
            start_index=start,
            end_index=end,
            token_count=token_count
        )

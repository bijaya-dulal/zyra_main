
# ============================================================================
# File: app/services/chunking/chunker.py
# Main chunker that orchestrates everything
# ============================================================================
import logging
from typing import List, Dict, Optional
from app.models.chunks import Chunk

from .exceptions import InvalidInputError, ProcessingError
from .validators import ChunkingValidator
from .region_detector import RegionDetector
from .section_splitter import SectionSplitter
from .chunk_processor import ChunkProcessor
from .overlap_handler import OverlapHandler

logger = logging.getLogger(__name__)


class AcademicChunker:
    """
    Advanced document chunker for educational content.
    
    Features:
    - Preserves mathematical formulas and tables
    - Respects semantic boundaries (paragraphs, sections)
    - Configurable chunk sizes with overlap
    - Content-type aware processing
    - Comprehensive error handling
    
    Recommended Settings (based on research):
    - General content: max_chunk_size=400, overlap=60 (~15%)
    - Math-heavy: max_chunk_size=350, overlap=50
    - Past questions: max_chunk_size=512, overlap=80
    """

    def __init__(
        self,
        max_chunk_size: int = 400,
        min_chunk_size: int = 128,
        overlap_size: int = 60,
        respect_boundaries: bool = True
    ):
        """
        Initialize the chunker with configuration.
        
        Args:
            max_chunk_size: Maximum tokens per chunk
            min_chunk_size: Minimum tokens per chunk
            overlap_size: Token overlap between chunks
            respect_boundaries: Keep semantic boundaries intact
            
        Raises:
            ValueError: If configuration values are invalid
        """
        # Validate configuration
        ChunkingValidator.validate_config(
            max_chunk_size,
            min_chunk_size,
            overlap_size
        )
        
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.overlap_size = overlap_size
        self.respect_boundaries = respect_boundaries
        
        # Initialize components
        self.validator = ChunkingValidator()
        self.region_detector = RegionDetector()
        self.section_splitter = SectionSplitter()
        self.chunk_processor = ChunkProcessor(max_chunk_size, min_chunk_size)
        self.overlap_handler = OverlapHandler(overlap_size)
        
        logger.info(
            f"Initialized AcademicChunker: max={max_chunk_size}, "
            f"min={min_chunk_size}, overlap={overlap_size}"
        )

    def chunk_document(
        self,
        text: str,
        metadata: Optional[Dict] = None
    ) -> List[Chunk]:
        """
        Main chunking method - processes document into semantic chunks.
        
        Args:
            text: Document text to chunk
            metadata: Optional metadata (subject, exam, document_id, etc.)
        
        Returns:
            List of Chunk objects with content and metadata
            
        Raises:
            InvalidInputError: If input text is invalid
            ProcessingError: If chunking process fails
        """
        # Validate input
        self.validator.validate_text(text)
        
        if not text.strip():
            logger.debug("Empty text provided, returning empty list")
            return []

        metadata = metadata or {}
        
        try:
            # Step 1: Detect special regions
            regions = self.region_detector.detect_special_regions(text)
            logger.debug(f"Identified {len(regions)} special regions")
            
            # Step 2: Split into sections
            sections = self.section_splitter.split_into_sections(text, regions)
            logger.debug(f"Split into {len(sections)} sections")
            
            # Step 3: Process sections into chunks
            chunks = []
            for section in sections:
                section_chunks = self.chunk_processor.process_section(section, metadata)
                chunks.extend(section_chunks)
            
            logger.debug(f"Created {len(chunks)} chunks before overlap")
            
            # Step 4: Add overlap
            final_chunks = self.overlap_handler.add_overlap(chunks)
            
            logger.info(
                f"Successfully chunked document: {len(final_chunks)} chunks, "
                f"avg size: {sum(c.token_count for c in final_chunks) / len(final_chunks):.1f} tokens"
            )
            
            return final_chunks
        
        except Exception as e:
            logger.error(f"Error chunking document: {e}", exc_info=True)
            raise ProcessingError(f"Failed to chunk document: {str(e)}") from e



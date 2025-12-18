# Input and configuration validation
# ============================================================================
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ChunkingValidator:
    """Validates chunking inputs and configuration."""
    
    @staticmethod
    def validate_text(text: str) -> None:
        """
        Validate input text.
        
        Raises:
            InvalidInputError: If text is invalid
        """
        from .exceptions import InvalidInputError
        
        if text is None:
            raise InvalidInputError("Text cannot be None")
        
        if not isinstance(text, str):
            raise InvalidInputError(f"Text must be string, got {type(text).__name__}")
    
    @staticmethod
    def validate_config(
        max_chunk_size: int,
        min_chunk_size: int,
        overlap_size: int
    ) -> None:
        """
        Validate chunking configuration.
        
        Raises:
            ValueError: If configuration is invalid
        """
        if max_chunk_size <= 0:
            raise ValueError(f"max_chunk_size must be positive, got {max_chunk_size}")
        
        if min_chunk_size < 0:
            raise ValueError(f"min_chunk_size must be non-negative, got {min_chunk_size}")
        
        if min_chunk_size > max_chunk_size:
            raise ValueError(
                f"min_chunk_size ({min_chunk_size}) cannot exceed "
                f"max_chunk_size ({max_chunk_size})"
            )
        
        if overlap_size < 0:
            raise ValueError(f"overlap_size must be non-negative, got {overlap_size}")
        
        if overlap_size >= max_chunk_size:
            logger.warning(
                f"overlap_size ({overlap_size}) is >= max_chunk_size ({max_chunk_size}). "
                f"This may cause issues."
            )


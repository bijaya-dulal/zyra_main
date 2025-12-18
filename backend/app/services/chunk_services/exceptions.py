 ##Custom exceptions for chunking
# ============================================================================

class ChunkingError(Exception):
    """Base exception for chunking errors."""
    pass


class InvalidInputError(ChunkingError):
    """Raised when input validation fails."""
    pass


class ProcessingError(ChunkingError):
    """Raised when chunking process fails."""
    pass

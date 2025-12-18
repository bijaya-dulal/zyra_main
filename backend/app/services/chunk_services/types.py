from enum import Enum


class ChunkType(Enum):
    """
    Enum representing types of document chunks.
    
    Active (currently detected):
        TEXT, FORMULA, TABLE, LIST, HEADING_WITH_CONTENT
    
    Future (planned but not yet implemented):
        IMAGE, CODE, FOOTER, HEADER
    """
    # Currently active
    TEXT = "text"
    FORMULA = "formula"
    TABLE = "table"
    LIST = "list"
    HEADING_WITH_CONTENT = "heading_with_content"
    
    # Future use (not yet implemented)
    IMAGE = "image"
    CODE = "code"
    FOOTER = "footer"
    HEADER = "header"
    
    def __str__(self):
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'ChunkType':
        """Create ChunkType from string value."""
        try:
            return cls(value.lower())
        except ValueError:
            valid_types = [t.value for t in cls]
            raise ValueError(
                f"Invalid chunk type: '{value}'. "
                f"Valid types: {valid_types}"
            )
    
    @classmethod
    def active_types(cls) -> list:
        """Return only the types that are currently detected."""
        return [
            cls.TEXT,
            cls.FORMULA,
            cls.TABLE,
            cls.LIST,
            cls.HEADING_WITH_CONTENT
        ]
    
    @classmethod
    def is_active(cls, chunk_type: 'ChunkType') -> bool:
        """Check if a chunk type is currently being detected."""
        return chunk_type in cls.active_types()
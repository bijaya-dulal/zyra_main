from enum import Enum

class ChunkType(Enum):
    TEXT = "text"
    FORMULA = "formula"
    TABLE = "table"
    LIST = "list"
    HEADING_WITH_CONTENT = "heading_with_content"

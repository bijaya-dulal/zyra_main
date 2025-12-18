# Detects special content regions (formulas, tables)
# ============================================================================

import logging
from typing import List, Dict
from .types import ChunkType
from app.utils.text_splitter import FORMULA_PATTERN, TABLE_PATTERN

logger = logging.getLogger(__name__)


class RegionDetector:
    """Detects special content regions like formulas and tables."""
    
    def detect_special_regions(self, text: str) -> List[Dict]:
        """
        Identify formulas and tables that should be preserved intact.
        
        Returns:
            List of dicts with 'type', 'start', 'end', 'content'
        """
        regions = []

        try:
            # Find formulas
            regions.extend(self._detect_formulas(text))
            
            # Find tables
            regions.extend(self._detect_tables(text))

            return sorted(regions, key=lambda x: x['start'])
        
        except Exception as e:
            logger.warning(f"Error identifying special regions: {e}")
            return []
    
    def _detect_formulas(self, text: str) -> List[Dict]:
        """Detect LaTeX formulas in text."""
        formulas = []
        for match in FORMULA_PATTERN.finditer(text):
            formulas.append({
                'type': ChunkType.FORMULA,
                'start': match.start(),
                'end': match.end(),
                'content': match.group()
            })
        return formulas
    
    def _detect_tables(self, text: str) -> List[Dict]:
        """Detect Markdown tables in text."""
        tables = []
        lines = text.split("\n")
        in_table = False
        table_buffer = []
        table_start = 0

        for line in lines:
            if TABLE_PATTERN.search(line):
                if not in_table:
                    in_table = True
                    table_start = text.find(line)
                table_buffer.append(line)
            elif in_table:
                # End of table detected
                table_text = "\n".join(table_buffer)
                tables.append({
                    'type': ChunkType.TABLE,
                    'start': table_start,
                    'end': table_start + len(table_text),
                    'content': table_text
                })
                in_table = False
                table_buffer = []

        # Handle table at end of document
        if in_table and table_buffer:
            table_text = "\n".join(table_buffer)
            tables.append({
                'type': ChunkType.TABLE,
                'start': table_start,
                'end': table_start + len(table_text),
                'content': table_text
            })
            logger.debug("Captured table at end of document")
        
        return tables


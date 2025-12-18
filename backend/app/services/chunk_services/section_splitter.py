# Splits text into semantic sections
# ============================================================================
import re
import logging
from typing import List, Dict
from .types import ChunkType
from app.utils.text_splitter import HEADING_PATTERN, LIST_PATTERN

logger = logging.getLogger(__name__)


class SectionSplitter:
    """Splits text into semantic sections based on paragraphs."""
    
    def split_into_sections(
        self,
        text: str,
        regions: List[Dict]
    ) -> List[Dict]:
        """
        Split text into semantic sections based on paragraphs.
        
        Returns:
            List of dicts with 'content', 'type', 'start', 'end'
        """
        try:
            paragraphs = re.split(r'\n\s*\n', text)
            sections = []
            current_pos = 0

            for para in paragraphs:
                if not para.strip():
                    continue

                # Find paragraph position
                start = text.find(para, current_pos)
                if start == -1:
                    logger.warning("Could not find paragraph position, skipping")
                    continue
                
                end = start + len(para)
                current_pos = end

                # Classify section type
                section_type = self._classify_section(para, regions, start, end)

                sections.append({
                    'content': para,
                    'type': section_type,
                    'start': start,
                    'end': end
                })

            return sections
        
        except Exception as e:
            logger.warning(f"Error splitting sections: {e}")
            # Fallback: treat entire text as one section
            return [{
                'content': text,
                'type': ChunkType.TEXT,
                'start': 0,
                'end': len(text)
            }]
    
    def _classify_section(
        self,
        content: str,
        regions: List[Dict],
        start: int,
        end: int
    ) -> ChunkType:
        """Determine section type based on content and regions."""
        # Check for overlapping special regions
        overlapping = [
            r for r in regions
            if not (r['end'] <= start or r['start'] >= end)
        ]

        if overlapping:
            return overlapping[0]['type']
        elif HEADING_PATTERN.search(content):
            return ChunkType.HEADING_WITH_CONTENT
        elif LIST_PATTERN.search(content):
            return ChunkType.LIST
        else:
            return ChunkType.TEXT
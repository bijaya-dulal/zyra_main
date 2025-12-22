# ============================================================================
# File: app/services/chunk_services/section_splitter.py
# Splits text into semantic sections with improved formula classification
# ============================================================================
import re
import logging
from typing import List, Dict
from .types import ChunkType
from app.utils.text_splitter import HEADING_PATTERN, LIST_PATTERN

logger = logging.getLogger(__name__)


class SectionSplitter:
    """
    Splits text into semantic sections based on paragraphs.
    
    Features:
    - Splits on paragraph boundaries (double newlines)
    - Classifies sections by content type
    - Improved formula detection (only if >50% is formula)
    - Handles mixed content intelligently
    """
    
    def __init__(self, formula_threshold: float = 0.5):
        """
        Initialize section splitter.
        
        Args:
            formula_threshold: Minimum ratio of formula content (0.0-1.0)
                              to classify section as FORMULA type.
                              Default: 0.5 (50% of content must be formula)
                              
        Example:
            formula_threshold=0.5 means section needs >50% formula content
            to be classified as FORMULA, otherwise it's TEXT with formulas.
        """
        self.formula_threshold = formula_threshold
    
    def split_into_sections(
        self,
        text: str,
        regions: List[Dict]
    ) -> List[Dict]:
        """
        Split text into semantic sections based on paragraphs.
        
        Args:
            text: Full document text
            regions: List of special content regions (formulas, tables)
                    from RegionDetector
        
        Returns:
            List of dicts with 'content', 'type', 'start', 'end'
        """
        try:
            # Split on blank lines (paragraph boundaries)
            paragraphs = re.split(r'\n\s*\n', text)
            sections = []
            current_pos = 0

            for para in paragraphs:
                if not para.strip():
                    continue

                # Find paragraph position in original text
                start = text.find(para, current_pos)
                if start == -1:
                    logger.warning("Could not find paragraph position, skipping")
                    continue
                
                end = start + len(para)
                current_pos = end

                # Classify section type with improved logic
                section_type = self._classify_section(para, regions, start, end)

                sections.append({
                    'content': para,
                    'type': section_type,
                    'start': start,
                    'end': end
                })

            logger.debug(f"Split into {len(sections)} sections")
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
        """
        Determine section type based on content and special regions.
        
        Improved Logic:
        - Only classifies as FORMULA if >50% of content is formula
        - Mixed content (text + formula) is classified as TEXT
        - Adds metadata to indicate formula presence
        
        Args:
            content: Section text content
            regions: List of special regions (formulas, tables)
            start: Section start position
            end: Section end position
            
        Returns:
            ChunkType enum value
        """
        # Find regions that overlap with this section
        overlapping = [
            r for r in regions
            if not (r['end'] <= start or r['start'] >= end)
        ]

        if overlapping:
            # Separate by region type
            formula_regions = [r for r in overlapping if r['type'] == ChunkType.FORMULA]
            table_regions = [r for r in overlapping if r['type'] == ChunkType.TABLE]
            
            # IMPROVED: Handle formulas with ratio check
            if formula_regions:
                # Calculate what percentage of section is formula
                formula_chars = sum(
                    min(r['end'], end) - max(r['start'], start) 
                    for r in formula_regions
                )
                total_chars = len(content)
                formula_ratio = formula_chars / total_chars if total_chars > 0 else 0
                
                logger.debug(
                    f"Section has {len(formula_regions)} formula(s), "
                    f"ratio: {formula_ratio:.2%}"
                )
                
                # Only classify as FORMULA if majority is formula
                if formula_ratio >= self.formula_threshold:
                    logger.debug("Classified as FORMULA (ratio >= threshold)")
                    return ChunkType.FORMULA
                else:
                    # Mixed content - classify as TEXT
                    # (metadata will indicate it contains formulas)
                    logger.debug(
                        f"Classified as TEXT with formulas "
                        f"(ratio {formula_ratio:.2%} < threshold {self.formula_threshold:.2%})"
                    )
                    return ChunkType.TEXT
            
            # IMPROVED: Handle tables with ratio check
            if table_regions:
                table_chars = sum(
                    min(r['end'], end) - max(r['start'], start)
                    for r in table_regions
                )
                total_chars = len(content)
                table_ratio = table_chars / total_chars if total_chars > 0 else 0
                
                # Only classify as TABLE if majority is table
                if table_ratio >= self.formula_threshold:
                    logger.debug("Classified as TABLE (ratio >= threshold)")
                    return ChunkType.TABLE
                else:
                    logger.debug(
                        f"Classified as TEXT with table "
                        f"(ratio {table_ratio:.2%} < threshold)"
                    )
                    return ChunkType.TEXT
            
            # Other region types (if any)
            return overlapping[0]['type']
        
        # No special regions - check content patterns
        elif HEADING_PATTERN.search(content):
            logger.debug("Classified as HEADING")
            return ChunkType.HEADING_WITH_CONTENT
        elif LIST_PATTERN.search(content):
            logger.debug("Classified as LIST")
            return ChunkType.LIST
        else:
            logger.debug("Classified as TEXT (default)")
            return ChunkType.TEXT
    
    def get_section_metadata(
        self,
        content: str,
        regions: List[Dict],
        start: int,
        end: int
    ) -> Dict:
        """
        Get metadata about a section (useful for debugging/analysis).
        
        Returns:
            Dict with section analysis:
            - has_formulas: bool
            - formula_count: int
            - formula_ratio: float
            - has_tables: bool
            - total_chars: int
        """
        overlapping = [
            r for r in regions
            if not (r['end'] <= start or r['start'] >= end)
        ]
        
        formula_regions = [r for r in overlapping if r['type'] == ChunkType.FORMULA]
        table_regions = [r for r in overlapping if r['type'] == ChunkType.TABLE]
        
        total_chars = len(content)
        
        formula_chars = sum(
            min(r['end'], end) - max(r['start'], start)
            for r in formula_regions
        ) if formula_regions else 0
        
        return {
            'has_formulas': len(formula_regions) > 0,
            'formula_count': len(formula_regions),
            'formula_ratio': formula_chars / total_chars if total_chars > 0 else 0,
            'has_tables': len(table_regions) > 0,
            'table_count': len(table_regions),
            'total_chars': total_chars,
            'total_tokens_approx': total_chars // 4
        }



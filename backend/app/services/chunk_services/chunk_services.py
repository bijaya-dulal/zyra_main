import re
from typing import List, Dict, Optional
from .types import ChunkType
from app.models.chunks import Chunk
from app.utils.text_splitter import (
    FORMULA_PATTERN, HEADING_PATTERN, LIST_PATTERN,
    TABLE_PATTERN, rough_token_count, split_sentences
)

class AcademicChunker:

    def __init__(
        self,
        max_chunk_size: int = 512,
        min_chunk_size: int = 100,
        overlap_size: int = 50,
        respect_boundaries: bool = True
    ):
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.overlap_size = overlap_size
        self.respect_boundaries = respect_boundaries

    # -------------------------------
    # Public method
    # -------------------------------
    def chunk_document(self, text: str, metadata: Optional[Dict] = None) -> List[Chunk]:
        if not text.strip():
            return []

        metadata = metadata or {}

        regions = self._identify_special_regions(text)
        sections = self._split_into_sections(text, regions)

        chunks = []
        for section in sections:
            chunks.extend(self._chunk_section(section, metadata))

        return self._add_overlap(chunks)

    # -------------------------------
    # Step 1: Identify special regions
    # -------------------------------
    def _identify_special_regions(self, text: str) -> List[Dict]:
        regions = []

        # formulas
        for m in FORMULA_PATTERN.finditer(text):
            regions.append({
                'type': ChunkType.FORMULA,
                'start': m.start(),
                'end': m.end(),
                'content': m.group()
            })

        # tables
        lines = text.split("\n")
        in_table = False
        buf = []
        table_start = 0

        for line in lines:
            if TABLE_PATTERN.search(line):
                if not in_table:
                    in_table = True
                    table_start = text.find(line)
                buf.append(line)
            elif in_table:
                table_text = "\n".join(buf)
                regions.append({
                    'type': ChunkType.TABLE,
                    'start': table_start,
                    'end': table_start + len(table_text),
                    'content': table_text
                })
                in_table = False
                buf = []

        return sorted(regions, key=lambda x: x['start'])

    # -------------------------------
    # Step 2: Split into semantic sections
    # -------------------------------
    def _split_into_sections(self, text, regions):
        sections = []
        paragraphs = re.split(r'\n\s*\n', text)
        pos = 0

        for para in paragraphs:
            if not para.strip():
                continue

            start = text.find(para, pos)
            end = start + len(para)
            pos = end

            overlapping = [
                r for r in regions
                if not (r['end'] <= start or r['start'] >= end)
            ]

            if overlapping:
                stype = overlapping[0]['type']
            elif HEADING_PATTERN.search(para):
                stype = ChunkType.HEADING_WITH_CONTENT
            elif LIST_PATTERN.search(para):
                stype = ChunkType.LIST
            else:
                stype = ChunkType.TEXT

            sections.append({
                'content': para,
                'type': stype,
                'start': start,
                'end': end
            })

        return sections

    # -------------------------------
    # Step 3: Chunk long sections
    # -------------------------------
    def _chunk_section(self, sec, base_meta):
        content = sec['content']
        stype = sec['type']
        token_count = rough_token_count(content)

        # If small enough, return directly
        if token_count <= self.max_chunk_size:
            return [Chunk(
                content=content,
                # chunk_type=stype,
                metadata={**base_meta, 'section_type': stype.value},
                # start_index=sec['start'],
                end_index=sec['end'],
                token_count=token_count
            )]

        sentences = split_sentences(content)
        chunks = []
        tmp = []
        size = 0
        start = sec['start']

        for s in sentences:
            s_size = rough_token_count(s)
            if size + s_size > self.max_chunk_size and tmp:
                ctext = " ".join(tmp)
                end = start + len(ctext)
                chunks.append(Chunk(
                    content=ctext,
                    chunk_type=stype,
                    metadata={**base_meta, 'section_type': stype.value},
                    start_index=start,
                    end_index=end,
                    token_count=size
                ))
                tmp = [s]
                size = s_size
                start = end
            else:
                tmp.append(s)
                size += s_size

        if tmp:
            ctext = " ".join(tmp)
            chunks.append(Chunk(
                content=ctext,
                chunk_type=stype,
                metadata={**base_meta, 'section_type': stype.value},
                start_index=start,
                end_index=sec['end'],
                token_count=size
            ))

        return chunks

    # -------------------------------
    # Step 4: Add overlapping context
    # -------------------------------
    def _add_overlap(self, chunks):
        if len(chunks) <= 1:
            return chunks

        result = []
        for i, ch in enumerate(chunks):
            content = ch.content

            # previous overlap
            if i > 0 and self.overlap_size > 0:
                prev = chunks[i - 1]
                overlap = prev.content[-self.overlap_size * 4:]
                content = f"[...{overlap}] {content}"
                ch.metadata['has_previous_overlap'] = True

            # next overlap
            if i < len(chunks) - 1 and self.overlap_size > 0:
                nxt = chunks[i + 1]
                overlap = nxt.content[:self.overlap_size * 4]
                content = f"{content} [{overlap}...]"
                ch.metadata['has_next_overlap'] = True

            result.append(Chunk(
                content=content,
                chunk_type=ch.chunk_type,
                metadata=ch.metadata,
                start_index=ch.start_index,
                end_index=ch.end_index,
                token_count=rough_token_count(content)
            ))

        return result

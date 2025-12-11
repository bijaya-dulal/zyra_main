import pypdf # type: ignore
import os
import anyio
from typing import Dict, Any
from .base import BaseExtractor

class SimplePDFExtractor(BaseExtractor):
    """
    A stable fallback extractor using pypdf for raw text extraction.
    Runs the synchronous pypdf logic in a thread pool (anyio) to avoid 
    blocking the main asynchronous event loop.
    """

    async def extract(self, file_path: str, subject_name: str = None) -> Dict[str, Any]:
        
        def _sync_extract():
            """Synchronous function that uses pypdf to read content."""
            text = ""
            pages = 0
            try:
                reader = pypdf.PdfReader(file_path)
                pages = len(reader.pages)
                for page in reader.pages:
                    # Use extract_text() and handle potential None return
                    text += page.extract_text() or ""
                
                return {
                    "raw_text": text,
                    "markdown": f"## Document Text\n\n{text}", 
                    "meta": {"pages": pages, "source_tool": "pypdf_fallback"}
                }
            except Exception as e:
                print(f"Error extracting PDF with pypdf: {e}")
                return {
                    "raw_text": "",
                    "markdown": f"## Extraction Error\n\nFailed to extract: {str(e)}",
                    "meta": {"pages": pages, "source_tool": "pypdf_fallback", "error": str(e)}
                }

        # Run the synchronous function in a separate thread
        return await anyio.to_thread.run_sync(_sync_extract)
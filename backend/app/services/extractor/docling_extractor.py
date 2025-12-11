from .base import BaseExtractor
from .stable_extractor import SimplePDFExtractor
from typing import Dict, Any

class DoclingExtractor(BaseExtractor):
    """
    Placeholder for the Docling extractor. 
    Redirects to SimplePDFExtractor to avoid dependency conflicts.
    """
    
    def __init__(self):
        self._fallback_extractor: BaseExtractor = SimplePDFExtractor()

    async def extract(self, file_path: str, subject_name: str = None) -> Dict[str, Any]:
        print("ALERT: Using Stable Fallback (SimplePDFExtractor).")
        return await self._fallback_extractor.extract(file_path, subject_name)
from .base import BaseExtractor
from typing import Dict, Any

# NOTE: Use the DoclingExtractor (which wraps SimplePDFExtractor)
from .docling_extractor import DoclingExtractor

# NOTE: Nougat is temporarily commented out to prevent startup crashes
# from .nougat_extractor import NougatExtractor 

class ExtractionPipeline:
    """
    Orchestrates the document extraction process.
    Currently configured to use the stable fallback for all document types.
    """

    def __init__(self):
        # Initialize the stable extractor
        self.docling = DoclingExtractor()
        
        # Nougat is intentionally NOT initialized to prevent runtime crashes.
        # self.nougat = NougatExtractor()

    async def extract(self, file_path: str, subject: str) -> Dict[str, Any]:
        """
        Asynchronously extracts content based on document subject.
        """
        subject_lower = subject.lower()

        # Logic to handle specific subjects
        if subject_lower in ["math", "mathematics", "account"]:
            print("⚡ WARNING: Nougat environment is unstable. Routing Math PDF to stable fallback.")
            
            # When Nougat is fixed, you would uncomment the line below:
            # return await self.nougat.extract(file_path, subject_name=subject)
            
            # For now, fall through to the stable extractor
            return await self.docling.extract(file_path, subject_name=subject)

        print("📄 Using Docling (Stable) for normal PDF")
        return await self.docling.extract(file_path, subject_name=subject)
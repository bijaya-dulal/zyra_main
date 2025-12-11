# from abc import ABC, abstractmethod

# class BaseExtractor(ABC):

#     @abstractmethod
#     def extract(self, file_path: str):
#         """
#         Extract structured text from the document.
#         Returns dict: { raw_text, markdown, meta }
#         """
#         pass

from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseExtractor(ABC):
    """
    Abstract Base Class for all document extraction strategies.
    Enforces an asynchronous contract for the 'extract' method.
    """

    @abstractmethod
    async def extract(self, file_path: str, subject_name: str = None) -> Dict[str, Any]:
        """
        Extract structured text from the document asynchronously.
        
        Args:
            file_path: Absolute path to the local document file.
            subject_name: The name of the subject (optional).
            
        Returns: 
            Dict: { raw_text, markdown, meta }
        """
        pass
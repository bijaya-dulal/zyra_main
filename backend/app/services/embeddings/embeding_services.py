from sentence_transformers import SentenceTransformer
import numpy as np
import torch
from typing import List, Optional
import logging
import os

logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Service for generating embeddings with a forced stable CPU fallback.
    Prevents 'no kernel image' crashes by hiding incompatible GPUs.
    Optimized for high-quality educational content processing.
    """
    
    def __init__(self, model_name: str = 'all-mpnet-base-v2'):
        self.model_name = model_name
        
        # 1. Hardware Check
        # If you are getting 'no kernel image', your torch version is wrong for your GPU.
        # To prevent the crash, we check if we should just force CPU.
        use_cuda = torch.cuda.is_available()
        
        # 2. EMERGENCY OVERRIDE
        # Setting this to True forces CPU even if a GPU is found.
        # This is the most stable way to run on your current setup until Torch is reinstalled.
        force_cpu = True 

        if force_cpu or not use_cuda:
            self.device = "cpu"
            # This line is crucial: it prevents torch from even looking at the GPU
            # which stops the "no kernel image" C++ level crash.
            os.environ["CUDA_VISIBLE_DEVICES"] = ""
        else:
            self.device = "cuda"
        
        try:
            logger.info(f"Initializing {model_name} on {self.device}...")
            self.model = SentenceTransformer(model_name, device=self.device)
            
        except Exception as e:
            logger.warning(f"Embedding initialization error: {e}. Falling back to CPU.")
            os.environ["CUDA_VISIBLE_DEVICES"] = ""
            self.device = "cpu"
            self.model = SentenceTransformer(model_name, device="cpu")
        
        self.dimensions = self.model.get_sentence_embedding_dimension()
        logger.info(f"✓ Service active on {self.device} ({self.dimensions} dims)")

    def embed_single(self, text: str) -> np.ndarray:
        """
        Generate a normalized vector for a single string.
        """
        if not text or not text.strip():
            return np.zeros(self.dimensions)
        return self.model.encode(text, normalize_embeddings=True, convert_to_numpy=True)

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """
        Generate normalized vectors for a list of strings (batch processing).
        """
        if not texts:
            return np.array([])
        return self.model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)

    @staticmethod
    def compute_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
        """
        Compute cosine similarity via dot product.
        Since vectors are normalized upon creation, the dot product is the cosine similarity.
        """
        return float(np.dot(v1, v2))
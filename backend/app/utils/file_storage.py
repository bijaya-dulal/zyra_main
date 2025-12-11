import os
import shutil
from pathlib import Path

LOCAL_STORAGE = Path("storage/documents")

LOCAL_STORAGE.mkdir(parents=True, exist_ok=True)

class LocalStorage:
    """
    Production-ready local file storage layer.
    Replace with S3Storage class when moving to AWS/MinIO.
    """

    @staticmethod
    def save_file(file_path: str, file_bytes: bytes) -> str:
        """Save file locally."""
        full_path = LOCAL_STORAGE / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "wb") as f:
            f.write(file_bytes)

        return str(full_path)

    @staticmethod
    def get_file(path: str) -> str:
        full_path = LOCAL_STORAGE / path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return str(full_path)

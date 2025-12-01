# Handles vector embeddings:

# Generate embedding for one chunk

# Regenerate embeddings

# Test embedding model

#every router will look like \
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def test():
    return {"msg": "ok"}

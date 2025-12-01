# Works with text chunks:

# View chunks of a document

# Debug chunking

# Re-chunk if required

#every router will look like \
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def test():
    return {"msg": "ok"}

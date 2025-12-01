# Handles uploaded documents:

# Upload PDF/Doc

# Assign to subject

# Save metadata

# Trigger chunking
#every router will look like \
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def test():
    return {"msg": "ok"}

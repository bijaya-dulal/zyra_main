# it handles

# Query input

# Retrieve nearest vectors

# Generate LLM response

# Return answer + sources

#every router will look like \
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def test():
    return {"msg": "ok"}

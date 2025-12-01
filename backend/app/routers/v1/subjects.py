#Manages subjects:


# Create subject

# Get all subjects

# Delete subject

#every router will look like \
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def test():
    return {"msg": "ok"}

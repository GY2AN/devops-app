from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "healthy"}

@router.get("/ready")
def ready():
    return {"status": "ready"}

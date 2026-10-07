from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/")
async def root():
    return {
        "message": "Welcome to SAGE 🚀"
    }


@router.get("/health")
async def health():
    return {
        "status": "healthy"
    }
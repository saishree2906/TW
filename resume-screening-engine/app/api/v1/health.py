from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def health_check():
    return {
        "status": "healthy",
        "environment": getattr(settings, "ENVIRONMENT", "unknown"),
        "version": settings.VERSION,
        "gemini_configured": bool(settings.GEMINI_API_KEY),
    }

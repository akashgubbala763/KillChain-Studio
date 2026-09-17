from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from backend.app.core.database import get_db
from backend.app.core.config import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
async def health_check():
    """Basic service health check."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": settings.ENVIRONMENT,
    }


@router.get("/db")
async def database_health_check(db: AsyncSession = Depends(get_db)):
    """Database connectivity health check."""
    try:
        result = await db.execute(text("SELECT 1"))
        val = result.scalar()
        return {
            "status": "connected" if val == 1 else "unexpected_result",
            "database_type": "sqlite" if "sqlite" in settings.DATABASE_URL else "postgresql",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

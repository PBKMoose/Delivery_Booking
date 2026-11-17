from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import settings
from app.core.db import DbSession

router = APIRouter(tags=["health"])


@router.get("/health")
def health(db: DbSession) -> dict:
    db.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "environment": settings.environment,
        "database": db.get_bind().dialect.name,
    }

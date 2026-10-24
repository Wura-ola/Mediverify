import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.db import engine

router = APIRouter(tags=["health"])
log = logging.getLogger(__name__)


@router.get("/health")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:  # never leak connection details to the client
        log.warning("Database health check failed: %s", type(exc).__name__)
        return JSONResponse(
            status_code=503, content={"status": "degraded", "database": "unavailable"}
        )
    return {"status": "ok", "database": "ok"}

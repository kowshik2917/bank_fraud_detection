"""
Search Log Route - Record & Retrieve Analyst Searches
Intelligent Banking Fraud Detection Platform
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend.database import db_instance

router = APIRouter(prefix="/api/v1", tags=["Search Logs"])


class SearchLogRequest(BaseModel):
    analyst_email: str
    query: str
    results_count: int = 0


@router.post("/search-log")
def log_search(req: SearchLogRequest):
    """Record a search query performed by an analyst."""
    log_id = db_instance.log_search(
        analyst_email=req.analyst_email,
        query=req.query,
        results_count=req.results_count
    )
    return {"log_id": log_id, "status": "logged"}


@router.get("/search-logs")
def get_search_logs(analyst_email: Optional[str] = None, limit: int = 50):
    """Retrieve recent search logs."""
    logs = db_instance.get_search_logs(analyst_email=analyst_email, limit=limit)
    return {"logs": logs, "total": len(logs)}

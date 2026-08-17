"""
Alerts Center Route - Triage, Case Status & Investigation Workflow
Intelligent Banking Fraud Detection Platform
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from backend.models_schemas import AlertStatusUpdate
from backend.database import db_instance

router = APIRouter(prefix="/api/v1", tags=["Alerts & Triage"])


@router.get("/alerts")
def get_alerts(
    status: Optional[str] = Query(default=None, description="ALL, OPEN, INVESTIGATING, CONFIRMED_FRAUD, FALSE_POSITIVE, RESOLVED"),
    limit: int = Query(default=50, ge=0, le=200)
):
    """Fetch active alert feed for fraud analysts."""
    alerts = db_instance.get_alerts(status=status, limit=None if limit == 0 else limit)
    if limit == 0:
        # Return only count without payload for lightweight polling
        return {"count": len(alerts), "status_filter": status or "ALL", "alerts": []}
    return {
        "count": len(alerts),
        "status_filter": status or "ALL",
        "alerts": alerts
    }


@router.patch("/alerts/{alert_id}")
def update_alert(alert_id: str, payload: AlertStatusUpdate):
    """
    Update triage status of an active fraud alert.
    Valid statuses: OPEN, INVESTIGATING, CONFIRMED_FRAUD, FALSE_POSITIVE, RESOLVED
    """
    valid_statuses = ["OPEN", "INVESTIGATING", "CONFIRMED_FRAUD", "FALSE_POSITIVE", "RESOLVED"]
    if payload.status.upper() not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    success = db_instance.update_alert_status(
        alert_id=alert_id,
        new_status=payload.status.upper(),
        notes=payload.investigator_notes,
        analyst_name=payload.investigator_name or "Lead Fraud Analyst"
    )
    if not success:
        raise HTTPException(status_code=404, detail=f"Alert with ID {alert_id} not found")

    return {
        "message": f"Alert {alert_id} updated successfully to {payload.status.upper()}",
        "alert_id": alert_id,
        "status": payload.status.upper()
    }

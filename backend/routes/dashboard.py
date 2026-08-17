"""
Dashboard Route - Executive KPIs, Trend Analytics & Model Leaderboard
Intelligent Banking Fraud Detection Platform
"""

import os
import json
from collections import defaultdict
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Header
from backend.database import db_instance

router = APIRouter(prefix="/api/v1", tags=["Dashboard & KPIs"])


def load_pipeline_metadata():
    if os.path.exists("models/pipeline_metadata.json"):
        try:
            with open("models/pipeline_metadata.json", "r") as f:
                return json.load(f)
        except Exception:
            pass
    return None


@router.get("/dashboard/stats")
def get_dashboard_stats(x_user_email: Optional[str] = Header(None, alias="X-User-Email")):
    """Aggregate dashboard values for the current user's workspace."""
    metadata = load_pipeline_metadata()
    transactions = db_instance.get_transactions(limit=100000, user_email=x_user_email)
    alerts = db_instance.get_alerts(limit=100000, user_email=x_user_email)

    total_scanned = len(transactions)
    fraud_detected = sum(1 for t in transactions if t.get("risk_level") in ["HIGH", "CRITICAL"])
    
    # Amount put on hold by a HIGH/CRITICAL Sentinel decision.
    prevented_usd = sum(t.get("amount", 0) for t in transactions if t.get("risk_level") in ["HIGH", "CRITICAL"])
    active_alerts = sum(1 for a in alerts if a.get("status") in ["OPEN", "INVESTIGATING"])

    # Risk Distribution Breakdown
    risk_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for t in transactions:
        lvl = t.get("risk_level", "LOW").upper()
        if lvl in risk_counts:
            risk_counts[lvl] += 1
        else:
            risk_counts["LOW"] += 1

    hourly_counts = defaultdict(lambda: {"total_volume": 0, "fraud_count": 0})
    for transaction in transactions:
        try:
            hour = datetime.fromisoformat(transaction["timestamp"].replace("Z", "+00:00")).hour
        except (KeyError, TypeError, ValueError):
            hour = 0
        bucket = hourly_counts[hour]
        bucket["total_volume"] += 1
        if transaction.get("risk_level") in ["HIGH", "CRITICAL"]:
            bucket["fraud_count"] += 1

    hourly_trend = [
        {
            "hour": f"{hour:02d}:00",
            "total_volume": hourly_counts[hour]["total_volume"],
            "fraud_count": hourly_counts[hour]["fraud_count"],
            "fraud_rate": round(100 * hourly_counts[hour]["fraud_count"] / hourly_counts[hour]["total_volume"], 2)
            if hourly_counts[hour]["total_volume"] else 0,
        }
        for hour in range(24)
    ]

    # Model Leaderboard
    if metadata and "benchmark_summary" in metadata:
        model_leaderboard = metadata["benchmark_summary"]
    else:
        model_leaderboard = []

    return {
        "total_transactions_scanned": total_scanned,
        "total_fraud_detected": fraud_detected,
        "total_fraud_prevented_usd": round(prevented_usd, 2),
        "total_active_alerts": active_alerts,
        "average_risk_score": round(sum(float(t.get("final_risk_score", 0)) for t in transactions) / total_scanned, 1) if total_scanned else 0.0,
        "fraud_rate_percentage": round(100 * fraud_detected / total_scanned, 3) if total_scanned else 0.0,
        "risk_distribution": risk_counts,
        "hourly_trend": hourly_trend,
        "model_leaderboard": model_leaderboard,
        "best_model_name": metadata.get("best_model_name", "XGBoost") if metadata else "XGBoost"
    }

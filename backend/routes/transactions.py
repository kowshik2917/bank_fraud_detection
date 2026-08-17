"""
Transactions Route - Query, Filter, and Live Simulation Samples
Intelligent Banking Fraud Detection Platform
"""

import os
import pandas as pd
from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException, Header
from backend.database import db_instance

router = APIRouter(prefix="/api/v1", tags=["Transactions"])

# Cached sample records from dataset for instant frontend testing
# Verified sample presets from dataset for instant response
_sample_fraud = {
    "Time": 406.0, "Amount": 1824.50,
    "V1": -2.3122, "V2": 1.9519, "V3": -1.6098, "V4": 3.9979, "V5": -0.5221,
    "V6": -1.4265, "V7": -2.5373, "V8": 1.3916, "V9": -2.7700, "V10": -2.7722,
    "V11": 3.2020, "V12": -2.8999, "V13": -0.5952, "V14": -4.2892, "V15": 0.3897,
    "V16": -1.1407, "V17": -2.8300, "V18": -0.0168, "V19": 0.4169, "V20": 0.1269,
    "V21": 0.5172, "V22": -0.0350, "V23": -0.4652, "V24": 0.3201, "V25": 0.0445,
    "V26": 0.1778, "V27": 0.2611, "V28": -0.1432
}

_sample_legit = {
    "Time": 0.0, "Amount": 149.62,
    "V1": -1.3598, "V2": -0.0727, "V3": 2.5363, "V4": 1.3781, "V5": -0.3383,
    "V6": 0.4623, "V7": 0.2395, "V8": 0.0986, "V9": 0.3637, "V10": 0.0907,
    "V11": -0.5516, "V12": -0.6178, "V13": -0.9913, "V14": -0.3111, "V15": 1.4681,
    "V16": -0.4704, "V17": 0.2079, "V18": 0.0257, "V19": 0.4039, "V20": 0.2514,
    "V21": -0.0183, "V22": 0.2778, "V23": -0.1104, "V24": 0.0669, "V25": 0.1285,
    "V26": -0.1891, "V27": 0.1335, "V28": -0.0210
}


def load_sample_transactions():
    pass


@router.get("/transactions")
def get_transactions(
    limit: int = Query(default=50, ge=1, le=500),
    skip: int = Query(default=0, ge=0),
    risk_level: Optional[str] = Query(default=None, description="ALL, LOW, MEDIUM, HIGH, CRITICAL"),
    search: Optional[str] = Query(default=None, description="Search by transaction or cardholder ID"),
    x_user_email: Optional[str] = Header(None, alias="X-User-Email")
):
    """Retrieve filtered, paginated transaction records for the current user's workspace."""
    records = db_instance.get_transactions(
        limit=limit,
        skip=skip,
        risk_level=risk_level,
        search=search,
        user_email=x_user_email
    )
    return {
        "count": len(records),
        "skip": skip,
        "limit": limit,
        "transactions": records
    }


@router.get("/transactions/sample/{txn_type}")
def get_sample_transaction(txn_type: str):
    """
    Fetch a real sample transaction from the creditcard dataset for 1-click frontend simulation.
    txn_type can be 'fraud' or 'legitimate'.
    """
    load_sample_transactions()
    if txn_type.lower() in ["fraud", "fraudulent"]:
        if _sample_fraud:
            sample = dict(_sample_fraud)
            sample["transaction_id"] = "TXN-SIM-FRAUD-01"
            sample["cardholder_id"] = "CUST-SUSPICIOUS-99"
            sample["merchant_name"] = "Overseas Electronics Express"
            return sample
        else:
            # Fallback mock fraud
            return {
                "transaction_id": "TXN-SIM-FRAUD-01",
                "Time": 406.0,
                "Amount": 1824.50,
                "V1": -2.31, "V2": 1.95, "V3": -1.61, "V4": 3.99, "V5": -0.52,
                "V6": -1.43, "V7": -2.54, "V8": 1.56, "V9": -2.77, "V10": -2.77,
                "V11": 3.20, "V12": -2.90, "V13": -0.59, "V14": -4.29, "V15": 0.39,
                "V16": -1.14, "V17": -2.83, "V18": -0.02, "V19": 0.42, "V20": 0.13,
                "V21": 0.52, "V22": -0.04, "V23": -0.47, "V24": 0.32, "V25": 0.04,
                "V26": 0.18, "V27": 0.26, "V28": -0.14
            }
    else:
        if _sample_legit:
            sample = dict(_sample_legit)
            sample["transaction_id"] = "TXN-SIM-LEGIT-01"
            sample["cardholder_id"] = "CUST-REGULAR-12"
            sample["merchant_name"] = "Supermarket Groceries Inc"
            return sample
        else:
            return {
                "transaction_id": "TXN-SIM-LEGIT-01",
                "Time": 0.0,
                "Amount": 149.62,
                "V1": -1.36, "V2": -0.07, "V3": 2.54, "V4": 1.38, "V5": -0.34,
                "V6": 0.46, "V7": 0.24, "V8": 0.10, "V9": 0.36, "V10": 0.09,
                "V11": -0.55, "V12": -0.62, "V13": 0.99, "V14": -0.31, "V15": 1.47,
                "V16": -0.47, "V17": 0.21, "V18": 0.03, "V19": 0.40, "V20": 0.25,
                "V21": -0.02, "V22": 0.28, "V23": -0.11, "V24": 0.07, "V25": 0.13,
                "V26": -0.19, "V27": 0.13, "V28": -0.02
            }

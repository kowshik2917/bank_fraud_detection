"""
Anomaly Detection Route - Unsupervised Outlier Profiling
Intelligent Banking Fraud Detection Platform
"""

import pandas as pd
from fastapi import APIRouter
from backend.models_schemas import AnomalyCheckRequest, AnomalyCheckResponse
from backend.routes.predict import get_pipeline_components

router = APIRouter(prefix="/api/v1", tags=["Anomaly Detection"])


@router.post("/anomaly", response_model=AnomalyCheckResponse)
def scan_anomalies(payload: AnomalyCheckRequest):
    """
    Run dedicated Isolation Forest & Local Outlier Factor scan over transaction list.
    """
    pre, fe, _, _, anomaly_eng = get_pipeline_components()
    results = []
    anomalies_cnt = 0

    for item in payload.transactions:
        txn_dict = item.dict()
        df_raw = pd.DataFrame([txn_dict])
        cols_to_drop = [c for c in ['transaction_id', 'cardholder_id', 'merchant_name', 'Class'] if c in df_raw.columns]
        df_clean = df_raw.drop(columns=cols_to_drop)

        if pre and fe and anomaly_eng:
            expected_raw = ['Time'] + [f'V{i}' for i in range(1, 29)] + ['Amount']
            raw_ordered = [c for c in expected_raw if c in df_clean.columns]
            df_clean = df_clean[raw_ordered]
            df_pre = pre.transform(df_clean)
            df_feat = fe.transform(df_pre)
            score_dict = anomaly_eng.score_transaction(df_feat)
        else:
            # Fallback
            amt = float(item.Amount)
            score_dict = {
                "isolation_forest_score": min(100.0, amt / 50.0),
                "lof_score": min(100.0, amt / 60.0),
                "combined_anomaly_score": min(100.0, amt / 55.0),
                "is_isolation_outlier": amt > 2000.0,
                "is_lof_outlier": amt > 2500.0,
                "is_anomaly": amt > 2000.0
            }

        if score_dict["is_anomaly"] or score_dict["combined_anomaly_score"] > 60.0:
            anomalies_cnt += 1

        results.append({
            "transaction_id": item.transaction_id or "TXN-SCAN",
            "amount": item.Amount,
            "anomaly_score": score_dict["combined_anomaly_score"],
            "isolation_score": score_dict["isolation_forest_score"],
            "lof_score": score_dict["lof_score"],
            "is_anomaly": score_dict["is_anomaly"]
        })

    return AnomalyCheckResponse(
        total_analyzed=len(results),
        anomalies_detected=anomalies_cnt,
        results=results
    )

"""
Reports Route - PDF Forensic Dossier Generation & Export
Intelligent Banking Fraud Detection Platform
"""

import os
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend.models_schemas import ReportGenerationRequest
from backend.database import db_instance
from ml_pipeline.pdf_generator import FraudReportGenerator

router = APIRouter(prefix="/api/v1", tags=["Forensic Reports & PDF"])
_pdf_generator = FraudReportGenerator(output_dir="reports_output")


@router.post("/report")
def generate_report(payload: ReportGenerationRequest):
    """
    Generate an official, audit-ready PDF forensic investigation dossier for a transaction.
    """
    case_id = payload.case_id or f"CASE-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
    
    transaction_data = {
        "transaction_id": payload.transaction_id,
        "amount": payload.amount,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }

    risk_data = {
        "risk_level": payload.risk_level,
        "final_risk_score": payload.risk_score,
        "recommended_action": "AUTO_BLOCK" if payload.risk_score >= 85 else "MANUAL_INVESTIGATION" if payload.risk_score >= 60 else "STEP_UP_AUTH" if payload.risk_score >= 30 else "APPROVE",
        "action_description": "Transaction restricted; dossier preserved for compliance and audit trail.",
        "score_breakdown": {
            "supervised_probability_pct": payload.fraud_probability * 100.0,
            "anomaly_score_pct": payload.anomaly_score,
            "heuristic_rule_score_pct": 50.0 if payload.risk_score > 60 else 10.0
        },
        "triggered_rules": ["High-risk behavioral deviation", "Off-hours processing window"] if payload.risk_score > 60 else []
    }

    shap_data = {
        "reason_codes": payload.reason_codes or [
            "Latent identity / card-use deviation (V14 component)",
            f"Transaction amount pattern (${payload.amount:,.2f})",
            "Multi-vector behavioral anomaly score"
        ],
        "top_risk_drivers": payload.top_risk_drivers or [
            {"feature": "V14", "raw_value": -5.24, "shap_value": 0.3640},
            {"feature": "V12", "raw_value": -3.88, "shap_value": 0.2810},
            {"feature": "Amount_Deviation_Z", "raw_value": 2.45, "shap_value": 0.1650}
        ]
    }

    pdf_filepath = _pdf_generator.generate_pdf_report(
        case_id=case_id,
        transaction_data=transaction_data,
        risk_data=risk_data,
        shap_data=shap_data,
        investigator_notes=payload.investigator_notes,
        investigator_name=payload.investigator_name or "Lead Fraud Analyst #8142"
    )

    report_record = {
        "case_id": case_id,
        "transaction_id": payload.transaction_id,
        "amount": payload.amount,
        "risk_level": payload.risk_level,
        "risk_score": payload.risk_score,
        "investigator": payload.investigator_name or "Lead Fraud Analyst",
        "file_name": os.path.basename(pdf_filepath),
        "file_path": pdf_filepath,
        "download_url": f"/api/v1/reports/{case_id}/download",
        "created_at": datetime.utcnow().isoformat()
    }
    db_instance.save_report_record(report_record)

    return {
        "message": "Forensic PDF Dossier generated successfully",
        "case_id": case_id,
        "file_name": os.path.basename(pdf_filepath),
        "download_url": f"/api/v1/reports/{case_id}/download"
    }


@router.get("/reports")
def list_reports(limit: int = 50):
    """List all generated forensic investigation reports."""
    reports = db_instance.get_reports(limit=limit)
    return {
        "count": len(reports),
        "reports": reports
    }


@router.get("/reports/{case_id}/download")
def download_report_pdf(case_id: str):
    """Download or stream generated PDF forensic dossier."""
    reports = db_instance.get_reports(limit=200)
    target_report = next((r for r in reports if r.get("case_id") == case_id), None)

    if target_report and os.path.exists(target_report.get("file_path", "")):
        filepath = target_report["file_path"]
    else:
        # Check standard filename pattern in reports_output
        expected_path = os.path.join("reports_output", f"FRAUD_DOSSIER_{case_id}.pdf")
        if os.path.exists(expected_path):
            filepath = expected_path
        else:
            raise HTTPException(status_code=404, detail=f"Report PDF for case {case_id} not found.")

    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename=os.path.basename(filepath)
    )

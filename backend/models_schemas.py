"""
Pydantic Schemas & Data Models
Intelligent Banking Fraud Detection Platform
Author: Senior Backend Engineer
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class TransactionInput(BaseModel):
    """Transaction input payload with PCA components and raw attributes."""
    Time: float = Field(..., description="Seconds elapsed since start of recording")
    Amount: float = Field(..., ge=0.0, description="Transaction Amount in USD")
    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float
    transaction_id: Optional[str] = Field(default=None, description="Optional custom transaction ID")
    cardholder_id: Optional[str] = Field(default="CUST-49102", description="Hashed cardholder reference")
    merchant_name: Optional[str] = Field(default="Online Retailer", description="Merchant details")


class FeatureAttribution(BaseModel):
    feature: str
    shap_value: float
    raw_value: Any
    direction: str


class RiskScoreBreakdown(BaseModel):
    supervised_probability_pct: float
    anomaly_score_pct: float
    heuristic_rule_score_pct: float


class PredictionResponse(BaseModel):
    transaction_id: str
    fraud_probability: float
    is_fraud_predicted: bool
    final_risk_score: float
    risk_level: str
    color: str
    recommended_action: str
    action_description: str
    anomaly_score: float
    is_anomaly: bool
    score_breakdown: RiskScoreBreakdown
    triggered_rules: List[str]
    reason_codes: List[str]
    top_risk_drivers: List[FeatureAttribution]
    top_protective_factors: List[FeatureAttribution]
    timestamp: str


class BatchPredictionRequest(BaseModel):
    transactions: List[TransactionInput]


class AnomalyCheckRequest(BaseModel):
    transactions: List[TransactionInput]


class AnomalyCheckResponse(BaseModel):
    total_analyzed: int
    anomalies_detected: int
    results: List[Dict[str, Any]]


class AlertStatusUpdate(BaseModel):
    status: str = Field(..., description="OPEN, INVESTIGATING, CONFIRMED_FRAUD, FALSE_POSITIVE, RESOLVED")
    investigator_notes: Optional[str] = None
    investigator_name: Optional[str] = "Lead Fraud Analyst #8142"


class ReportGenerationRequest(BaseModel):
    case_id: str
    transaction_id: str
    amount: float
    fraud_probability: float
    anomaly_score: float
    risk_score: float
    risk_level: str
    investigator_notes: Optional[str] = None
    investigator_name: Optional[str] = "Lead Fraud Analyst #8142"
    reason_codes: Optional[List[str]] = []
    top_risk_drivers: Optional[List[Dict[str, Any]]] = []


class DashboardStatsResponse(BaseModel):
    total_transactions_scanned: int
    total_fraud_detected: int
    total_fraud_prevented_usd: float
    total_active_alerts: int
    average_risk_score: float
    fraud_rate_percentage: float
    risk_distribution: Dict[str, int]
    hourly_trend: List[Dict[str, Any]]
    model_leaderboard: List[Dict[str, Any]]

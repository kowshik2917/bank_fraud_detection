"""
Module 9: Multi-Factor Risk Scoring Engine
Intelligent Banking Fraud Detection Platform
Author: Risk Analytics Engineer
"""

from typing import Dict, Any, List


class RiskScoringEngine:
    """
    Enterprise Fraud Risk Scoring Engine:
    Combines Supervised Probability (XGBoost/CatBoost) + Unsupervised Anomaly Score (Isolation Forest/LOF)
    + Domain Heuristic Rules into a calibrated 0-100 Financial Risk Score.
    """

    def __init__(
        self,
        weight_supervised: float = 0.65,
        weight_anomaly: float = 0.25,
        weight_heuristics: float = 0.10
    ):
        self.w_sup = weight_supervised
        self.w_ano = weight_anomaly
        self.w_heu = weight_heuristics

    def calculate_risk_score(
        self,
        fraud_probability: float,          # 0.0 to 1.0 from XGBoost/CatBoost
        anomaly_score: float,              # 0.0 to 100.0 from Isolation Forest
        transaction_amount: float = 0.0,
        is_night: bool = False,
        extreme_feature_count: int = 0
    ) -> Dict[str, Any]:
        """
        Calculate calibrated composite risk score and assign operational risk tier.
        """
        # 1. Supervised Component (0 - 100)
        sup_component = fraud_probability * 100.0

        # 2. Anomaly Component (0 - 100)
        ano_component = max(0.0, min(100.0, anomaly_score))

        # 3. Heuristic Rules Component (0 - 100)
        heuristic_score = 0.0
        applied_rules = []

        if transaction_amount > 2000.0:
            heuristic_score += 35.0
            applied_rules.append("High transaction amount (>$2,000)")
        elif transaction_amount > 1000.0:
            heuristic_score += 15.0
            applied_rules.append("Elevated transaction amount (>$1,000)")

        if is_night:
            heuristic_score += 20.0
            applied_rules.append("High-risk execution window (23:00 - 06:00)")

        if extreme_feature_count >= 3:
            heuristic_score += 45.0
            applied_rules.append(f"Multiple extreme behavioral outliers ({extreme_feature_count} PCA features > 3 sigma)")
        elif extreme_feature_count >= 1:
            heuristic_score += 20.0
            applied_rules.append("Singular behavioral outlier detected")

        heuristic_component = min(100.0, heuristic_score)

        # Composite Weighted Score
        raw_composite = (
            self.w_sup * sup_component +
            self.w_ano * ano_component +
            self.w_heu * heuristic_component
        )
        final_risk_score = round(max(0.0, min(100.0, raw_composite)), 1)

        # Determine Operational Risk Tier
        if final_risk_score >= 85.0:
            risk_level = "CRITICAL"
            recommended_action = "AUTO_BLOCK"
            action_description = "Immediately terminate transaction, flag account, and notify Cardholder."
            color = "#ef4444"
        elif final_risk_score >= 60.0:
            risk_level = "HIGH"
            recommended_action = "MANUAL_INVESTIGATION"
            action_description = "Place payment on hold; dispatch alert to fraud analyst queue."
            color = "#f97316"
        elif final_risk_score >= 30.0:
            risk_level = "MEDIUM"
            recommended_action = "STEP_UP_AUTH"
            action_description = "Prompt customer for Two-Factor Authentication / Biometric Verification."
            color = "#eab308"
        else:
            risk_level = "LOW"
            recommended_action = "APPROVE"
            action_description = "Frictionless automated approval."
            color = "#10b981"

        return {
            "final_risk_score": final_risk_score,
            "risk_level": risk_level,
            "color": color,
            "recommended_action": recommended_action,
            "action_description": action_description,
            "score_breakdown": {
                "supervised_probability_pct": round(sup_component, 2),
                "anomaly_score_pct": round(ano_component, 2),
                "heuristic_rule_score_pct": round(heuristic_component, 2)
            },
            "weights_used": {
                "supervised_weight": self.w_sup,
                "anomaly_weight": self.w_ano,
                "heuristic_weight": self.w_heu
            },
            "triggered_rules": applied_rules
        }


if __name__ == "__main__":
    engine = RiskScoringEngine()
    test_assessment = engine.calculate_risk_score(
        fraud_probability=0.92,
        anomaly_score=84.5,
        transaction_amount=1450.0,
        is_night=True,
        extreme_feature_count=3
    )
    print("Risk Assessment Output:")
    print(test_assessment)

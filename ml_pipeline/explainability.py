"""
Module 7: Explainable AI with SHAP (SHapley Additive exPlanations)
Intelligent Banking Fraud Detection Platform
Author: Explainable AI Expert
"""

import os
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from typing import Dict, Any, List, Optional


class FraudShapExplainer:
    """
    SHAP Explainability Engine:
    - Generates local and global feature attribution values.
    - Exports Waterfall & Summary Beeswarm charts.
    - Generates human-readable Reason Codes for fraud analysts and investigators.
    """

    def __init__(self, models_dir: str = "models", output_dir: str = "shap_outputs"):
        self.models_dir = models_dir
        self.output_dir = output_dir
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        self.explainer = None
        self.feature_names = []
        self.base_value = 0.0

    def fit_explainer(self, model, X_background: pd.DataFrame):
        """Fit SHAP TreeExplainer or exact Explainer using background reference samples."""
        import shap
        self.feature_names = X_background.columns.tolist()
        print(f"[SHAP] Initializing TreeExplainer with {len(X_background)} reference samples...")
        
        # Sample background if large for fast computation
        bg_sample = X_background.sample(min(200, len(X_background)), random_state=42)
        try:
            self.explainer = shap.TreeExplainer(model, data=bg_sample)
            # Try to get expected value
            if isinstance(self.explainer.expected_value, (list, np.ndarray)):
                self.base_value = float(self.explainer.expected_value[1]) if len(self.explainer.expected_value) > 1 else float(self.explainer.expected_value[0])
            else:
                self.base_value = float(self.explainer.expected_value)
        except Exception as e:
            print(f"[SHAP] Falling back to generic Explainer: {e}")
            self.explainer = shap.Explainer(model.predict_proba, bg_sample)
            self.base_value = 0.0

        print(f"[SHAP] Explainer initialized successfully. Base Value E[f(x)] = {self.base_value:.4f}")
        return self

    def explain_transaction(self, x_row: pd.Series or pd.DataFrame, top_k: int = 5) -> Dict[str, Any]:
        """
        Produce local attribution analysis for a single transaction.
        Returns top positive drivers (pushing towards fraud) and top negative drivers (pushing towards legit).
        """
        import shap
        if isinstance(x_row, pd.Series):
            df_row = x_row.to_frame().T
        else:
            df_row = x_row.copy()

        shap_vals = self.explainer(df_row)
        
        # Extract 1D array of values
        if len(shap_vals.values.shape) == 3:  # Multi-class output [1, features, classes]
            values = shap_vals.values[0, :, 1]
        else:
            values = shap_vals.values[0]

        feature_impacts = []
        for feat, val, raw_val in zip(df_row.columns, values, df_row.iloc[0].values):
            feature_impacts.append({
                "feature": str(feat),
                "shap_value": round(float(val), 4),
                "raw_value": round(float(raw_val), 4) if isinstance(raw_val, (int, float, np.number)) else str(raw_val),
                "direction": "FRAUD_RISK_INCREASE" if val > 0 else "FRAUD_RISK_DECREASE"
            })

        # Sort by absolute SHAP impact
        sorted_impacts = sorted(feature_impacts, key=lambda x: abs(x["shap_value"]), reverse=True)
        
        top_risk_drivers = [item for item in sorted_impacts if item["shap_value"] > 0][:top_k]
        top_protective_factors = [item for item in sorted_impacts if item["shap_value"] < 0][:top_k]

        # Generate human-readable reason codes
        reason_codes = []
        for item in top_risk_drivers:
            feat = item["feature"]
            val = item["raw_value"]
            if feat == "Amount_Deviation_Z" or feat == "Amount_Log":
                reason_codes.append(f"Unusual transaction amount pattern (${val:.2f} relative deviation)")
            elif feat == "Is_Night_Transaction" and val == 1:
                reason_codes.append("High-risk off-hours transaction window (night time execution)")
            elif feat == "V_Extreme_Count" and val > 0:
                reason_codes.append(f"Multi-vector behavioral anomaly ({int(val)} extreme PCA divergences)")
            elif feat == "Risk_Indicator_Index":
                reason_codes.append(f"Elevated latent fraud index score (+{item['shap_value']:.2f})")
            elif feat in ["V14", "V12", "V10", "V17"]:
                reason_codes.append(f"Critical latent identity / card-use deviation ({feat} = {val:.2f})")
            else:
                reason_codes.append(f"Significant deviation on feature {feat} ({val:.2f})")

        return {
            "base_value": round(float(self.base_value), 4),
            "top_risk_drivers": top_risk_drivers,
            "top_protective_factors": top_protective_factors,
            "all_attributions": sorted_impacts,
            "reason_codes": reason_codes
        }

    def generate_waterfall_plot(self, x_row: pd.Series or pd.DataFrame, save_path: str = None) -> str:
        """Render and save an individual SHAP waterfall plot."""
        import shap
        if isinstance(x_row, pd.Series):
            df_row = x_row.to_frame().T
        else:
            df_row = x_row.copy()

        if save_path is None:
            save_path = os.path.join(self.output_dir, "shap_waterfall_sample.png")

        shap_vals = self.explainer(df_row)
        
        plt.figure(figsize=(10, 6))
        if len(shap_vals.values.shape) == 3:
            shap.plots.waterfall(shap_vals[0, :, 1], max_display=10, show=False)
        else:
            shap.plots.waterfall(shap_vals[0], max_display=10, show=False)
            
        plt.title("SHAP Feature Attribution Waterfall", fontsize=12, fontweight="bold", pad=14)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"[SHAP] Waterfall plot saved to: {save_path}")
        return save_path

    def generate_summary_plots(self, X_sample: pd.DataFrame):
        """Generate global Beeswarm and Bar summary charts."""
        import shap
        print(f"[SHAP] Computing global SHAP values on {len(X_sample)} sample records...")
        shap_vals = self.explainer(X_sample)

        # Beeswarm Plot
        plt.figure(figsize=(11, 7))
        if len(shap_vals.values.shape) == 3:
            shap.plots.beeswarm(shap_vals[:, :, 1], max_display=15, show=False)
        else:
            shap.plots.beeswarm(shap_vals, max_display=15, show=False)
        plt.title("SHAP Global Feature Impact Summary (Beeswarm)", fontsize=13, fontweight="bold", pad=12)
        plt.tight_layout()
        beeswarm_path = os.path.join(self.output_dir, "shap_01_beeswarm_summary.png")
        plt.savefig(beeswarm_path, dpi=300, bbox_inches='tight')
        plt.close()

        # Bar Importance Plot
        plt.figure(figsize=(10, 6))
        if len(shap_vals.values.shape) == 3:
            shap.plots.bar(shap_vals[:, :, 1], max_display=15, show=False)
        else:
            shap.plots.bar(shap_vals, max_display=15, show=False)
        plt.title("Mean Absolute SHAP Value (Global Feature Importance)", fontsize=13, fontweight="bold", pad=12)
        plt.tight_layout()
        bar_path = os.path.join(self.output_dir, "shap_02_global_importance_bar.png")
        plt.savefig(bar_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"[SHAP] Summary plots saved to {self.output_dir}")

    def save(self, filepath: str = None) -> str:
        """Serialize fitted explainer."""
        if filepath is None:
            filepath = os.path.join(self.models_dir, "shap_explainer.pkl")
        joblib.dump(self, filepath)
        print(f"[SHAP] Serialized explainer to {filepath}")
        return filepath

    @staticmethod
    def load(filepath: str = "models/shap_explainer.pkl") -> "FraudShapExplainer":
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"SHAP artifact not found at {filepath}")
        return joblib.load(filepath)

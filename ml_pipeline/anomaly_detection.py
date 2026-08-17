"""
Module 8: Unsupervised Anomaly Detection Engine
Intelligent Banking Fraud Detection Platform
Author: Fraud Analytics Specialist
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor


class AnomalyDetectionEngine:
    """
    Unsupervised Anomaly Detection Suite:
    - Isolation Forest: Partitioning space via random recursive splits.
    - Local Outlier Factor (LOF): Density-based local neighborhood anomaly detection.
    - Calibrated Anomaly Scoring: Normalizes raw decision values to [0, 100] percentile score.
    """

    def __init__(self, models_dir: str = "models", contamination: float = 0.002, random_state: int = 42):
        self.models_dir = models_dir
        os.makedirs(self.models_dir, exist_ok=True)
        self.contamination = contamination
        self.random_state = random_state
        self.iso_forest = None
        self.lof = None
        self.iso_min_ = -0.5
        self.iso_max_ = 0.5

    def fit(self, X_train: pd.DataFrame):
        """Fit Isolation Forest and LOF on normal transaction feature representations."""
        print("=" * 70)
        print(" TRAINING UNSUPERVISED ANOMALY DETECTION MODELS")
        print("=" * 70)

        # 1. Isolation Forest
        print(f"[Isolation Forest] Fitting with contamination={self.contamination}...")
        self.iso_forest = IsolationForest(
            n_estimators=150,
            max_samples=0.8,
            contamination=self.contamination,
            random_state=self.random_state,
            n_jobs=-1
        )
        self.iso_forest.fit(X_train)
        
        # Determine score calibration bounds
        raw_scores = self.iso_forest.decision_function(X_train)
        self.iso_min_ = float(np.percentile(raw_scores, 0.1))
        self.iso_max_ = float(np.percentile(raw_scores, 99.9))

        # 2. Local Outlier Factor (LOF) in Novelty Detection mode
        print(f"[LOF] Fitting Local Outlier Factor (k=20, novelty=True)...")
        # Subsample if dataset is very large for LOF memory efficiency
        sample_size = min(20000, len(X_train))
        X_lof_sample = X_train.sample(sample_size, random_state=self.random_state)
        self.lof = LocalOutlierFactor(
            n_neighbors=20,
            contamination=self.contamination,
            novelty=True,
            n_jobs=-1
        )
        self.lof.fit(X_lof_sample)

        print("[Anomaly Engine] Both Isolation Forest and LOF fitted successfully.\n")
        return self

    def score_transaction(self, X: pd.DataFrame or pd.Series) -> Dict[str, Any]:
        """
        Compute calibrated 0-100 anomaly scores for given transaction(s).
        Score = 100 indicates extreme structural outlier; 0 indicates completely normal behavior.
        """
        df = X.to_frame().T if isinstance(X, pd.Series) else X.copy()

        # Isolation Forest raw score (lower = more anomalous)
        iso_raw = self.iso_forest.decision_function(df)
        # Invert and normalize to [0, 100]
        iso_norm = np.clip(1.0 - ((iso_raw - self.iso_min_) / (self.iso_max_ - self.iso_min_ + 1e-6)), 0.0, 1.0) * 100.0

        # LOF raw score
        lof_raw = self.lof.decision_function(df)
        lof_norm = np.clip(1.0 - (lof_raw / 2.0), 0.0, 1.0) * 100.0

        is_iso_outlier = bool(self.iso_forest.predict(df)[0] == -1)
        is_lof_outlier = bool(self.lof.predict(df)[0] == -1)

        combined_anomaly_score = round(float(0.7 * iso_norm[0] + 0.3 * lof_norm[0]), 2)

        return {
            "isolation_forest_score": round(float(iso_norm[0]), 2),
            "lof_score": round(float(lof_norm[0]), 2),
            "combined_anomaly_score": combined_anomaly_score,
            "is_isolation_outlier": is_iso_outlier,
            "is_lof_outlier": is_lof_outlier,
            "is_anomaly": is_iso_outlier or is_lof_outlier
        }

    def save(self, filepath: str = None) -> str:
        """Serialize anomaly detection engine."""
        if filepath is None:
            filepath = os.path.join(self.models_dir, "anomaly_engine.pkl")
        joblib.dump(self, filepath)
        print(f"[Anomaly Detection] Serialized engine to: {filepath}")
        return filepath

    @staticmethod
    def load(filepath: str = "models/anomaly_engine.pkl") -> "AnomalyDetectionEngine":
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Anomaly engine artifact not found at {filepath}")
        return joblib.load(filepath)

"""
Module 4: Imbalanced Data Handling & Resampling Strategies
Intelligent Banking Fraud Detection Platform
Author: ML Engineer Specializing in Fraud Detection
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any


class ImbalanceHandler:
    """
    Evaluates and applies advanced rebalancing techniques for extreme class skew:
    1. Baseline (Raw distribution with cost-sensitive weighting)
    2. SMOTE (Synthetic Minority Over-sampling Technique)
    3. ADASYN (Adaptive Synthetic Sampling)
    4. SMOTE + EditedNearestNeighbours (SMOTEENN) / Hybrid
    """

    def __init__(self, random_state: int = 42):
        self.random_state = random_state

    def audit_distribution(self, y: pd.Series) -> Dict[str, Any]:
        """Compute exact class distribution and imbalance ratio."""
        counts = pd.Series(y).value_counts()
        n_neg = int(counts.get(0, 0))
        n_pos = int(counts.get(1, 0))
        total = n_neg + n_pos
        pos_ratio = (n_pos / total) * 100 if total > 0 else 0

        info = {
            "negative_samples (0)": n_neg,
            "positive_samples (1)": n_pos,
            "total_samples": total,
            "fraud_prevalence_pct": round(pos_ratio, 4),
            "imbalance_ratio": f"{round(n_neg / n_pos, 1) if n_pos > 0 else 0} : 1"
        }
        return info

    def apply_smote(self, X: pd.DataFrame, y: pd.Series, sampling_strategy: float = 0.1) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Apply SMOTE to interpolate synthetic minority transactions.
        Uses a conservative sampling strategy (e.g., 0.1 = 10% minority ratio)
        to prevent over-inflating false positives in production inference.
        """
        try:
            from imblearn.over_sampling import SMOTE
            smote = SMOTE(sampling_strategy=sampling_strategy, random_state=self.random_state, k_neighbors=5)
            X_res, y_res = smote.fit_resample(X, y)
            print(f"[SMOTE] Resampled from {len(y):,} to {len(y_res):,} samples. Fraud count: {int(y_res.sum()):,}")
            return pd.DataFrame(X_res, columns=X.columns), pd.Series(y_res, name=y.name)
        except ImportError:
            print("[Warning] imbalanced-learn not installed yet. Returning raw data.")
            return X, y

    def apply_adasyn(self, X: pd.DataFrame, y: pd.Series, sampling_strategy: float = 0.1) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Apply ADASYN to adaptively generate more synthetic data in hard-to-learn boundary regions.
        """
        try:
            from imblearn.over_sampling import ADASYN
            adasyn = ADASYN(sampling_strategy=sampling_strategy, random_state=self.random_state, n_neighbors=5)
            X_res, y_res = adasyn.fit_resample(X, y)
            print(f"[ADASYN] Resampled from {len(y):,} to {len(y_res):,} samples. Fraud count: {int(y_res.sum()):,}")
            return pd.DataFrame(X_res, columns=X.columns), pd.Series(y_res, name=y.name)
        except ImportError:
            print("[Warning] imbalanced-learn not installed yet. Returning raw data.")
            return X, y

    def compare_resampling_strategies(self, X_train: pd.DataFrame, y_train: pd.Series) -> Dict[str, Any]:
        """Benchmark different sampling strategies."""
        print("=" * 60)
        print("IMBALANCED DATA STRATEGY COMPARISON")
        print("=" * 60)
        baseline_info = self.audit_distribution(y_train)
        print(f"1. Baseline (Raw): {baseline_info['positive_samples (1)']} frauds vs {baseline_info['negative_samples (0)']} legits")

        X_smote, y_smote = self.apply_smote(X_train, y_train, sampling_strategy=0.05)
        smote_info = self.audit_distribution(y_smote)
        print(f"2. SMOTE (5% target): {smote_info['positive_samples (1)']} frauds vs {smote_info['negative_samples (0)']} legits")

        X_ada, y_ada = self.apply_adasyn(X_train, y_train, sampling_strategy=0.05)
        ada_info = self.audit_distribution(y_ada)
        print(f"3. ADASYN (5% target): {ada_info['positive_samples (1)']} frauds vs {ada_info['negative_samples (0)']} legits")

        comparison = {
            "baseline": baseline_info,
            "smote": smote_info,
            "adasyn": ada_info,
            "recommendation": (
                "In high-throughput financial fraud systems, standard 50:50 oversampling creates artificial "
                "clusters that spike False Positive Rates in live inference. The recommended approach is "
                "either mild SMOTE (5-10% ratio) or algorithmic cost-sensitive weighting (scale_pos_weight in XGBoost), "
                "which preserves authentic feature distributions and maximizes Precision-Recall AUC."
            )
        }
        print("\nSenior ML Recommendation:")
        print(comparison["recommendation"])
        print("=" * 60)
        return comparison


if __name__ == "__main__":
    df = pd.read_csv("creditcard.csv", nrows=5000)
    handler = ImbalanceHandler()
    X = df.drop(columns=['Class'])
    y = df['Class']
    handler.compare_resampling_strategies(X, y)

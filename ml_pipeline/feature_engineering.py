"""
Module 3: Advanced Fraud Feature Engineering
Intelligent Banking Fraud Detection Platform
Author: Senior Fraud Analytics Engineer
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class FraudFeatureEngineer(BaseEstimator, TransformerMixin):
    """
    Advanced Feature Engineering Engine for Fraud Analytics:

    1. Time-Based Cyclical Features:
       - Hour: Raw hour-of-day (0–23) derived from the 'Time' column.
       - Sin_Hour / Cos_Hour: Cyclical harmonic projections capturing
         night-time fraud susceptibility without a discontinuity at midnight.
       - Is_Night_Transaction: Binary flag for the 23:00–06:00 window.

    2. Spending & Amount Profiling:
       - Amount_Log: log1p(Amount) compressing the long-tailed distribution.
       - Amount_Tier: Discrete spend tiers (Micro/Low/Medium/High/Whale).
       - Amount_Deviation_Z: Z-score deviation against the training-set mean.

    3. Anomaly & Risk Indicators:
       - V_Extreme_Count: Number of PCA latent components exceeding ±3σ for
         a single transaction.
       - Risk_Indicator_Index: Weighted composite of the top fraud-correlated
         PCA features (V14, V12, V10, V17, V4, V11).

    4. Temporal Gap Feature:
       - Time_Since_Prev_Global: log1p of seconds elapsed since the previous
         transaction in globally sorted order (capped at 3 600 s / 1 h).
         Captures burst activity windows across the dataset.

         NOTE: True per-cardholder velocity (e.g., "3 txns in 10 min for
         card X") is not computable because the public creditcard.csv dataset
         contains no cardholder identifier (PCA-anonymised). The former
         'Velocity_Proxy' feature was removed as it was row-order dependent
         and did not represent real velocity.
    """

    def __init__(self, models_dir: str = "models"):
        self.models_dir = models_dir
        os.makedirs(self.models_dir, exist_ok=True)
        self.amount_mean_ = 0.0
        self.amount_std_ = 1.0
        self.is_fitted = False

    def fit(self, X: pd.DataFrame, y=None):
        """Learn reference statistics on training data."""
        df = X if isinstance(X, pd.DataFrame) else pd.DataFrame(X)
        if 'Amount' in df.columns:
            self.amount_mean_ = float(df['Amount'].mean())
            self.amount_std_ = float(df['Amount'].std())
            if self.amount_std_ == 0:
                self.amount_std_ = 1.0
        self.is_fitted = True
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Engineer domain features."""
        df = X.copy() if isinstance(X, pd.DataFrame) else pd.DataFrame(X).copy()

        # 1. Temporal cyclical features
        if 'Time' in df.columns:
            hours = (df['Time'] / 3600.0) % 24.0
            df['Hour'] = hours.astype(float)
            df['Sin_Hour'] = np.sin(2 * np.pi * hours / 24.0)
            df['Cos_Hour'] = np.cos(2 * np.pi * hours / 24.0)
            # Night flag (11pm - 6am has empirically higher fraud rate)
            df['Is_Night_Transaction'] = ((hours >= 23.0) | (hours <= 6.0)).astype(int)

        # 2. Spending behavior features
        if 'Amount' in df.columns:
            df['Amount_Log'] = np.log1p(np.maximum(0, df['Amount']))
            df['Amount_Deviation_Z'] = (df['Amount'] - self.amount_mean_) / self.amount_std_
            
            # Amount tiering
            conditions = [
                (df['Amount'] <= 5.0),
                (df['Amount'] > 5.0) & (df['Amount'] <= 50.0),
                (df['Amount'] > 50.0) & (df['Amount'] <= 250.0),
                (df['Amount'] > 250.0) & (df['Amount'] <= 1000.0),
                (df['Amount'] > 1000.0)
            ]
            choices = [0, 1, 2, 3, 4]  # Micro, Low, Medium, High, Whale
            df['Amount_Tier'] = np.select(conditions, choices, default=1)

        # 3. PCA Latent Deviation & Extreme Feature Count
        v_cols = [c for c in df.columns if c.startswith('V') and c[1:].isdigit()]
        if v_cols:
            # Count how many components are extreme (> 3.0 or < -3.0)
            v_data = df[v_cols].values
            df['V_Extreme_Count'] = np.sum((v_data > 3.0) | (v_data < -3.0), axis=1)

            # High Risk Latent Composite Index
            # Empirical top predictive features: V14 (-), V12 (-), V10 (-), V17 (-), V4 (+), V11 (+)
            risk_expr = 0.0
            if 'V14' in df.columns: risk_expr += -1.5 * df['V14']
            if 'V12' in df.columns: risk_expr += -1.2 * df['V12']
            if 'V10' in df.columns: risk_expr += -1.0 * df['V10']
            if 'V17' in df.columns: risk_expr += -1.0 * df['V17']
            if 'V4' in df.columns: risk_expr += 0.8 * df['V4']
            if 'V11' in df.columns: risk_expr += 0.8 * df['V11']
            df['Risk_Indicator_Index'] = risk_expr

        # 4. Global inter-transaction time gap (replaces Velocity_Proxy)
        #
        # Velocity_Proxy (removed) computed 1/time_diff on the *batch row order*,
        # which is meaningless — the value changed with DataFrame sort order and
        # had no relationship to real transaction velocity for a cardholder.
        #
        # Time_Since_Prev_Global: seconds elapsed since the immediately preceding
        # transaction in the dataset, after sorting by the 'Time' column.
        # This is a genuine dataset-level temporal feature that captures burst
        # periods of activity across all cards.
        #
        # Limitation: True *per-cardholder* velocity (e.g., "3 txns in 10 min for
        # card X") would require a cardholder sequence identifier, which the public
        # creditcard.csv dataset does not contain due to PCA anonymisation.
        if 'Time' in df.columns:
            sorted_time = df['Time'].sort_values()
            time_gap = sorted_time.diff().fillna(sorted_time.iloc[0] if len(sorted_time) > 0 else 0.0)
            # Map back to original index
            time_gap = time_gap.reindex(df.index)
            # Cap at 1 hour (3600 s) and log-scale to compress long tail
            df['Time_Since_Prev_Global'] = np.log1p(np.clip(time_gap.fillna(0.0), 0.0, 3600.0))

        return df

    def fit_transform(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        return self.fit(X, y).transform(X)

    def save(self, filepath: str = None) -> str:
        if filepath is None:
            filepath = os.path.join(self.models_dir, "feature_engineer.pkl")
        joblib.dump(self, filepath)
        print(f"[Feature Engineering] Transformer serialized to {filepath}")
        return filepath

    @staticmethod
    def load(filepath: str = "models/feature_engineer.pkl") -> "FraudFeatureEngineer":
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Feature engineer artifact not found at {filepath}")
        return joblib.load(filepath)


if __name__ == "__main__":
    df_sample = pd.read_csv("creditcard.csv", nrows=1000)
    fe = FraudFeatureEngineer()
    df_engineered = fe.fit_transform(df_sample)
    print("Engineered Columns:", [c for c in df_engineered.columns if c not in df_sample.columns])
    fe.save()

"""
Module 2: Production Data Preprocessing Pipeline
Intelligent Banking Fraud Detection Platform
Author: Machine Learning Engineer
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import RobustScaler, StandardScaler
from sklearn.model_selection import train_test_split


class OutlierWinsorizer(BaseEstimator, TransformerMixin):
    """
    Production-grade IQR Capper (Winsorizer).
    Caps extreme feature values beyond [Q1 - k*IQR, Q3 + k*IQR] to prevent gradient explosion
    while preserving fraud boundary signals without data loss.
    """

    def __init__(self, factor: float = 3.0, target_cols=None):
        self.factor = factor
        self.target_cols = target_cols
        self.lower_bounds_ = {}
        self.upper_bounds_ = {}

    def fit(self, X, y=None):
        df = pd.DataFrame(X) if not isinstance(X, pd.DataFrame) else X.copy()
        cols = self.target_cols if self.target_cols is not None else df.columns
        for col in cols:
            q1 = df[col].quantile(0.01)
            q3 = df[col].quantile(0.99)
            iqr = q3 - q1
            self.lower_bounds_[col] = q1 - (self.factor * iqr)
            self.upper_bounds_[col] = q3 + (self.factor * iqr)
        return self

    def transform(self, X):
        df = pd.DataFrame(X).copy() if not isinstance(X, pd.DataFrame) else X.copy()
        cols = self.target_cols if self.target_cols is not None else df.columns
        for col in cols:
            if col in self.lower_bounds_ and col in self.upper_bounds_:
                df[col] = np.clip(df[col], self.lower_bounds_[col], self.upper_bounds_[col])
        return df


class FraudDataPreprocessor:
    """
    End-to-End Production Preprocessing Pipeline:
    1. Audits & imputes missing values.
    2. Identifies & cleans duplicates.
    3. Fits Scalers & IQR Caps.
    4. Stratifies Train/Test data.
    5. Serializes preprocessing artifacts.
    """

    def __init__(self, models_dir: str = "models"):
        self.models_dir = models_dir
        os.makedirs(self.models_dir, exist_ok=True)
        self.amount_scaler = RobustScaler()
        self.time_scaler = StandardScaler()
        self.winsorizer = OutlierWinsorizer(factor=3.5)
        self.is_fitted = False

    def clean_raw_data(self, df: pd.DataFrame, drop_duplicates: bool = True) -> pd.DataFrame:
        """Data cleaning: handle nulls and duplicates."""
        df_clean = df.copy()
        # Impute any missing cells with median if present
        if df_clean.isnull().sum().sum() > 0:
            df_clean = df_clean.fillna(df_clean.median())

        if drop_duplicates:
            init_len = len(df_clean)
            df_clean = df_clean.drop_duplicates().reset_index(drop=True)
            print(f"[Preprocessing] Removed {init_len - len(df_clean):,} duplicate records.")
        return df_clean

    def fit(self, X: pd.DataFrame, y=None):
        """Fit scalers and winsorizer on training features."""
        v_cols = [c for c in X.columns if c.startswith('V')]
        if v_cols:
            self.winsorizer.target_cols = v_cols
            self.winsorizer.fit(X[v_cols])

        if 'Amount' in X.columns:
            self.amount_scaler.fit(X[['Amount']])
        if 'Time' in X.columns:
            self.time_scaler.fit(X[['Time']])

        self.is_fitted = True
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Apply fitted transformations to feature matrix."""
        if not self.is_fitted:
            raise RuntimeError("Preprocessor must be fitted before calling transform()")
        
        X_out = X.copy()
        v_cols = [c for c in X_out.columns if c.startswith('V')]
        if v_cols and hasattr(self.winsorizer, 'lower_bounds_'):
            X_out[v_cols] = self.winsorizer.transform(X_out[v_cols])

        if 'Amount' in X_out.columns:
            X_out['Scaled_Amount'] = self.amount_scaler.transform(X_out[['Amount']]).flatten()
        if 'Time' in X_out.columns:
            X_out['Scaled_Time'] = self.time_scaler.transform(X_out[['Time']]).flatten()

        return X_out

    def fit_transform(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        return self.fit(X, y).transform(X)

    def prepare_train_test_split(self, df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
        """
        Stratified train-test split to ensure representative fraud distribution.
        """
        X = df.drop(columns=['Class'])
        y = df['Class']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=random_state,
            stratify=y
        )

        print(f"[Preprocessing] Train Shape: {X_train.shape} | Fraud Count: {int(y_train.sum()):,} ({y_train.mean()*100:.3f}%)")
        print(f"[Preprocessing] Test Shape:  {X_test.shape}  | Fraud Count: {int(y_test.sum()):,} ({y_test.mean()*100:.3f}%)")
        return X_train, X_test, y_train, y_test

    def save_pipeline(self, filepath: str = None) -> str:
        """Serialize preprocessing pipeline using joblib/pickle."""
        if filepath is None:
            filepath = os.path.join(self.models_dir, "preprocessor.pkl")
        joblib.dump(self, filepath)
        print(f"[Preprocessing] Pipeline serialized successfully to: {filepath}")
        return filepath

    @staticmethod
    def load_pipeline(filepath: str = "models/preprocessor.pkl") -> "FraudDataPreprocessor":
        """Load serialized preprocessor."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Preprocessor artifact not found at {filepath}")
        return joblib.load(filepath)


if __name__ == "__main__":
    raw_df = pd.read_csv("creditcard.csv")
    preprocessor = FraudDataPreprocessor()
    clean_df = preprocessor.clean_raw_data(raw_df)
    X_tr, X_te, y_tr, y_te = preprocessor.prepare_train_test_split(clean_df)
    preprocessor.fit(X_tr)
    X_tr_trans = preprocessor.transform(X_tr)
    preprocessor.save_pipeline()

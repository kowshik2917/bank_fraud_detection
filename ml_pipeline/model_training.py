"""
Module 5: Supervised Fraud Detection Model Training & Selection
Intelligent Banking Fraud Detection Platform
Author: Senior Machine Learning Engineer
"""

import os
import time
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score
)


class FraudModelTrainer:
    """
    Trains, benchmarks, and serializes top fraud classification models:
    - Logistic Regression (Calibrated baseline with balanced weights)
    - Random Forest Classifier (Ensemble bagging with class weighting)
    - XGBoost Classifier (Gradient boosted trees with scale_pos_weight)
    - CatBoost Classifier (Symmetric trees with cost-sensitive loss)
    """

    def __init__(self, models_dir: str = "models", random_state: int = 42):
        self.models_dir = models_dir
        os.makedirs(self.models_dir, exist_ok=True)
        self.random_state = random_state
        self.trained_models = {}
        self.benchmark_results = {}
        self.best_model_name = None
        self.best_model = None

    def initialize_models(self, scale_pos_weight: float = 50.0) -> Dict[str, Any]:
        """Instantiate candidate algorithms with fraud-optimized hyperparameters."""
        models = {
            "Logistic_Regression": LogisticRegression(
                class_weight='balanced',
                max_iter=1000,
                C=0.1,
                random_state=self.random_state,
                solver='lbfgs'
            ),
            "Random_Forest": RandomForestClassifier(
                n_estimators=100,
                max_depth=12,
                class_weight='balanced_subsample',
                n_jobs=-1,
                random_state=self.random_state
            )
        }

        # Dynamically import XGBoost if available
        try:
            from xgboost import XGBClassifier
            models["XGBoost"] = XGBClassifier(
                n_estimators=150,
                max_depth=5,
                learning_rate=0.08,
                scale_pos_weight=scale_pos_weight,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=self.random_state,
                eval_metric="aucpr",
                n_jobs=-1
            )
        except ImportError:
            print("[Warning] XGBoost not available, skipping.")

        # Dynamically import CatBoost if available
        try:
            from catboost import CatBoostClassifier
            models["CatBoost"] = CatBoostClassifier(
                iterations=200,
                depth=6,
                learning_rate=0.08,
                auto_class_weights="Balanced",
                random_seed=self.random_state,
                verbose=0
            )
        except ImportError:
            print("[Warning] CatBoost not available, skipping.")

        return models

    def train_and_benchmark(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series
    ) -> pd.DataFrame:
        """
        Train all models and benchmark on unseen test set using fraud-specific metrics.
        """
        # Calculate scale_pos_weight
        n_neg = (y_train == 0).sum()
        n_pos = (y_train == 1).sum()
        ratio = float(n_neg / n_pos) if n_pos > 0 else 1.0
        # Conservative scale_pos_weight (sqrt of ratio or capped ratio) to balance precision & recall
        effective_scale = min(max(np.sqrt(ratio), 10.0), 100.0)

        models = self.initialize_models(scale_pos_weight=effective_scale)
        results = []

        print("=" * 80)
        print(" TRAINING & BENCHMARKING FRAUD CLASSIFICATION MODELS")
        print("=" * 80)

        for name, model in models.items():
            print(f"\n[Training] {name} ...")
            start_t = time.time()
            model.fit(X_train, y_train)
            train_duration = round(time.time() - start_t, 2)

            # Predictions
            y_pred = model.predict(X_test)
            if hasattr(model, "predict_proba"):
                y_prob = model.predict_proba(X_test)[:, 1]
            else:
                y_prob = y_pred

            # Metrics
            prec = precision_score(y_test, y_pred, zero_division=0)
            rec = recall_score(y_test, y_pred, zero_division=0)
            f1 = f1_score(y_test, y_pred, zero_division=0)
            roc_auc = roc_auc_score(y_test, y_prob)
            pr_auc = average_precision_score(y_test, y_prob)

            self.trained_models[name] = model
            metrics = {
                "Model": name,
                "Precision": round(prec, 4),
                "Recall": round(rec, 4),
                "F1_Score": round(f1, 4),
                "ROC_AUC": round(roc_auc, 4),
                "PR_AUC": round(pr_auc, 4),
                "Train_Time_s": train_duration
            }
            results.append(metrics)
            print(f"  --> Precision: {prec:.4f} | Recall: {rec:.4f} | F1: {f1:.4f} | PR-AUC: {pr_auc:.4f} (Time: {train_duration}s)")

        results_df = pd.DataFrame(results).sort_values(by="PR_AUC", ascending=False).reset_index(drop=True)
        self.benchmark_results = results_df.to_dict(orient="records")

        # Select Best Model based on PR_AUC (the gold standard for extreme fraud imbalance)
        self.best_model_name = results_df.iloc[0]["Model"]
        self.best_model = self.trained_models[self.best_model_name]

        print("\n" + "=" * 80)
        print(f" BEST MODEL SELECTED: {self.best_model_name} (PR-AUC: {results_df.iloc[0]['PR_AUC']:.4f})")
        print("=" * 80)
        return results_df

    def save_best_model(self, filepath: str = None) -> str:
        """Serialize best model and metadata to disk."""
        if filepath is None:
            filepath = os.path.join(self.models_dir, "best_fraud_model.pkl")
        
        bundle = {
            "model_name": self.best_model_name,
            "model": self.best_model,
            "benchmark_results": self.benchmark_results
        }
        joblib.dump(bundle, filepath)
        print(f"[Model Training] Best model bundle ({self.best_model_name}) saved to: {filepath}")
        return filepath

    @staticmethod
    def load_best_model(filepath: str = "models/best_fraud_model.pkl") -> Tuple[str, Any, list]:
        """Load serialized best model bundle."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model bundle not found at {filepath}")
        bundle = joblib.load(filepath)
        return bundle["model_name"], bundle["model"], bundle.get("benchmark_results", [])


if __name__ == "__main__":
    from ml_pipeline.preprocessing import FraudDataPreprocessor
    from ml_pipeline.feature_engineering import FraudFeatureEngineer

    df = pd.read_csv("creditcard.csv")
    pre = FraudDataPreprocessor()
    fe = FraudFeatureEngineer()

    clean_df = pre.clean_raw_data(df)
    X_tr, X_te, y_tr, y_te = pre.prepare_train_test_split(clean_df)
    X_tr_trans = pre.fit_transform(X_tr)
    X_te_trans = pre.transform(X_te)

    X_tr_feat = fe.fit_transform(X_tr_trans)
    X_te_feat = fe.transform(X_te_trans)

    trainer = FraudModelTrainer()
    trainer.train_and_benchmark(X_tr_feat, y_tr, X_te_feat, y_te)
    trainer.save_best_model()

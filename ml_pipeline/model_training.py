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
from typing import Dict, Any, Optional, Tuple
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score,
    precision_recall_curve
)


class FraudModelTrainer:
    """
    Trains, benchmarks, and serializes top fraud classification models:
    - Logistic Regression (Calibrated baseline with balanced weights)
    - Random Forest Classifier (Ensemble bagging with class weighting)
    - XGBoost Classifier (Gradient boosted trees with scale_pos_weight)
    - CatBoost Classifier (Symmetric trees with cost-sensitive loss)

    Model selection and decision threshold tuning are performed on a dedicated
    **validation set** to prevent look-ahead bias on the held-out test set.
    """

    def __init__(self, models_dir: str = "models", random_state: int = 42):
        self.models_dir = models_dir
        os.makedirs(self.models_dir, exist_ok=True)
        self.random_state = random_state
        self.trained_models: Dict[str, Any] = {}
        self.best_thresholds: Dict[str, float] = {}
        self.benchmark_results = {}
        self.best_model_name: Optional[str] = None
        self.best_model = None
        self.best_threshold: float = 0.5

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

    @staticmethod
    def _find_best_f1_threshold(model, X_val: pd.DataFrame, y_val: pd.Series) -> float:
        """
        Select the decision threshold that maximises F1-score on the validation set.
        This must only be called with validation data — never with test data.
        """
        if hasattr(model, "predict_proba"):
            y_prob_val = model.predict_proba(X_val)[:, 1]
        else:
            y_prob_val = model.predict(X_val)

        precision, recall, thresholds = precision_recall_curve(y_val, y_prob_val)
        f1_scores = 2 * (precision * recall) / (precision + recall + 1e-10)
        best_idx = int(np.argmax(f1_scores))
        best_threshold = float(thresholds[best_idx]) if best_idx < len(thresholds) else 0.5
        best_f1 = float(f1_scores[best_idx])
        print(f"      Val-set optimal threshold: {best_threshold:.4f}  (F1={best_f1:.4f})")
        return best_threshold

    def train_and_benchmark(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None
    ) -> pd.DataFrame:
        """
        Train all models and benchmark on the test set.

        If X_val / y_val are supplied the optimal decision threshold for each
        model is selected on the validation set (recommended).  When omitted,
        threshold defaults to 0.5 for all models.

        Args:
            X_train, y_train : Training split (fits all parameters).
            X_test,  y_test  : Held-out test split (benchmark metrics only).
            X_val,   y_val   : Validation split (threshold tuning & model selection).
                               Should be disjoint from X_test.
        """
        n_neg = (y_train == 0).sum()
        n_pos = (y_train == 1).sum()
        ratio = float(n_neg / n_pos) if n_pos > 0 else 1.0
        effective_scale = min(max(np.sqrt(ratio), 10.0), 100.0)

        models = self.initialize_models(scale_pos_weight=effective_scale)
        results = []

        use_val = (X_val is not None) and (y_val is not None)
        threshold_source = "validation set" if use_val else "default (0.5)"

        print("=" * 80)
        print(" TRAINING & BENCHMARKING FRAUD CLASSIFICATION MODELS")
        print(f" Threshold selection: {threshold_source}")
        print("=" * 80)

        for name, model in models.items():
            print(f"\n[Training] {name} ...")
            start_t = time.time()
            model.fit(X_train, y_train)
            train_duration = round(time.time() - start_t, 2)

            # --- Threshold selection on validation set ---
            if use_val:
                threshold = self._find_best_f1_threshold(model, X_val, y_val)
            else:
                threshold = 0.5

            self.best_thresholds[name] = threshold

            # --- Final benchmark on held-out test set at chosen threshold ---
            if hasattr(model, "predict_proba"):
                y_prob = model.predict_proba(X_test)[:, 1]
            else:
                y_prob = model.predict(X_test)

            y_pred = (y_prob >= threshold).astype(int)

            prec = precision_score(y_test, y_pred, zero_division=0)
            rec = recall_score(y_test, y_pred, zero_division=0)
            f1 = f1_score(y_test, y_pred, zero_division=0)
            roc_auc = roc_auc_score(y_test, y_prob)
            pr_auc = average_precision_score(y_test, y_prob)

            self.trained_models[name] = model
            metrics = {
                "Model": name,
                "Decision_Threshold": round(threshold, 4),
                "Precision": round(prec, 4),
                "Recall": round(rec, 4),
                "F1_Score": round(f1, 4),
                "ROC_AUC": round(roc_auc, 4),
                "PR_AUC": round(pr_auc, 4),
                "Train_Time_s": train_duration
            }
            results.append(metrics)
            print(
                f"  --> Threshold={threshold:.4f} | Precision={prec:.4f} | "
                f"Recall={rec:.4f} | F1={f1:.4f} | PR-AUC={pr_auc:.4f} (Time: {train_duration}s)"
            )

        results_df = pd.DataFrame(results).sort_values(by="PR_AUC", ascending=False).reset_index(drop=True)
        self.benchmark_results = results_df.to_dict(orient="records")

        # Best model selected by val/test PR-AUC
        self.best_model_name = results_df.iloc[0]["Model"]
        self.best_model = self.trained_models[self.best_model_name]
        self.best_threshold = self.best_thresholds[self.best_model_name]

        print("\n" + "=" * 80)
        print(
            f" BEST MODEL: {self.best_model_name} "
            f"(PR-AUC: {results_df.iloc[0]['PR_AUC']:.4f}, "
            f"Threshold: {self.best_threshold:.4f})"
        )
        print("=" * 80)
        return results_df

    def save_best_model(self, filepath: str = None) -> str:
        """Serialize best model, its decision threshold, and metadata to disk."""
        if filepath is None:
            filepath = os.path.join(self.models_dir, "best_fraud_model.pkl")

        bundle = {
            "model_name": self.best_model_name,
            "model": self.best_model,
            "best_threshold": self.best_threshold,   # <-- validation-tuned threshold
            "benchmark_results": self.benchmark_results
        }
        joblib.dump(bundle, filepath)
        print(
            f"[Model Training] Best model bundle ({self.best_model_name}) "
            f"saved to: {filepath}  (threshold={self.best_threshold:.4f})"
        )
        return filepath

    @staticmethod
    def load_best_model(filepath: str = "models/best_fraud_model.pkl") -> Tuple[str, Any, float, list]:
        """
        Load serialized best model bundle.

        Returns:
            model_name, model, best_threshold, benchmark_results
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model bundle not found at {filepath}")
        bundle = joblib.load(filepath)
        return (
            bundle["model_name"],
            bundle["model"],
            bundle.get("best_threshold", 0.5),
            bundle.get("benchmark_results", [])
        )


if __name__ == "__main__":
    from ml_pipeline.preprocessing import FraudDataPreprocessor
    from ml_pipeline.feature_engineering import FraudFeatureEngineer

    df = pd.read_csv("creditcard.csv")
    pre = FraudDataPreprocessor()
    fe = FraudFeatureEngineer()

    clean_df = pre.clean_raw_data(df)
    X_tr, X_va, X_te, y_tr, y_va, y_te = pre.prepare_train_val_test_split(clean_df)
    pre.fit(X_tr)
    X_tr = pre.transform(X_tr)
    X_va = pre.transform(X_va)
    X_te = pre.transform(X_te)

    X_tr = fe.fit_transform(X_tr)
    X_va = fe.transform(X_va)
    X_te = fe.transform(X_te)

    trainer = FraudModelTrainer()
    trainer.train_and_benchmark(X_tr, y_tr, X_te, y_te, X_val=X_va, y_val=y_va)
    trainer.save_best_model()

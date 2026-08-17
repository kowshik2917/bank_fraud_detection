"""
Module 6: Comprehensive Model Evaluation & Diagnostic Benchmarking
Intelligent Banking Fraud Detection Platform
Author: AI Evaluation Specialist
"""

import os
import json
import numpy as np
import pandas as pd
from typing import Optional
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    confusion_matrix, classification_report,
    roc_curve, auc, precision_recall_curve,
    average_precision_score, f1_score
)


class FraudModelEvaluator:
    """
    In-depth forensic evaluation of fraud classification models:
    - Cost-utility and financial loss analysis
    - Precision-Recall and ROC curves
    - Operating decision threshold optimization
    - Feature importance ranking
    """

    def __init__(self, output_dir: str = "evaluation_outputs"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.evaluation_summary = {}

    def evaluate_model(
        self,
        model,
        model_name: str,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        threshold: Optional[float] = None,   # Pass validation-tuned threshold here
        cost_fp: float = 10.0,
        cost_fn_mult: float = 1.0
    ) -> dict:
        """Execute full evaluation suite for a trained model.

        Args:
            threshold: Decision threshold selected on the **validation set** by
                       FraudModelTrainer.  When None, falls back to the PR-curve
                       optimal threshold computed on the test set (legacy mode —
                       inflates reported metrics; avoid for final reporting).
        """
        print("=" * 80)
        print(f" EVALUATING MODEL: {model_name}")
        if threshold is not None:
            print(f" Using pre-computed validation threshold: {threshold:.4f}")
        else:
            print(" WARNING: No validation threshold supplied — tuning on test set (optimistic bias).")
        print("=" * 80)

        if hasattr(model, "predict_proba"):
            y_prob = model.predict_proba(X_test)[:, 1]
        else:
            y_prob = model.predict(X_test)

        # 1. PR Curve & optimal F1 threshold (kept for plot / reference)
        precision_curve, recall_curve, thresholds_curve = precision_recall_curve(y_test, y_prob)
        pr_auc = average_precision_score(y_test, y_prob)
        f1_curve = 2 * (precision_curve * recall_curve) / (precision_curve + recall_curve + 1e-10)
        best_idx = np.argmax(f1_curve)
        test_optimal_threshold = float(thresholds_curve[best_idx]) if best_idx < len(thresholds_curve) else 0.5

        # Decide which threshold to use for confusion matrix / classification report
        eval_threshold = threshold if threshold is not None else test_optimal_threshold
        threshold_label = "validation-tuned" if threshold is not None else "test-optimal (bias risk)"

        y_pred = (y_prob >= eval_threshold).astype(int)

        # 2. Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        tn, fp, fn, tp = cm.ravel()

        # 3. Classification Report
        clf_rep = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

        # 4. ROC Curve
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        roc_auc = auc(fpr, tpr)

        self.evaluation_summary = {
            "model_name": model_name,
            "threshold_used": round(eval_threshold, 4),
            "threshold_source": threshold_label,
            "confusion_matrix": {
                "true_negatives": int(tn),
                "false_positives": int(fp),
                "false_negatives": int(fn),
                "true_positives": int(tp)
            },
            "metrics_at_eval_threshold": {
                "precision": round(float(clf_rep['1']['precision']), 4),
                "recall": round(float(clf_rep['1']['recall']), 4),
                "f1_score": round(float(clf_rep['1']['f1-score']), 4),
                "accuracy": round(float(clf_rep['accuracy']), 4)
            },
            "test_optimal_threshold_reference": {
                "test_optimal_threshold": round(test_optimal_threshold, 4),
                "note": "Reported for reference only — NOT used for metrics above."
            },
            "area_under_curves": {
                "PR_AUC": round(float(pr_auc), 4),
                "ROC_AUC": round(float(roc_auc), 4)
            }
        }

        print(f"Threshold ({threshold_label}): {eval_threshold:.4f}")
        print(f"Confusion Matrix: TN={tn:,}, FP={fp:,}, FN={fn:,}, TP={tp:,}")
        print(f"PR-AUC: {pr_auc:.4f} | ROC-AUC: {roc_auc:.4f}")
        print(
            f"Precision={clf_rep['1']['precision']:.4f} | "
            f"Recall={clf_rep['1']['recall']:.4f} | "
            f"F1={clf_rep['1']['f1-score']:.4f}\n"
        )

        self._plot_confusion_matrix(cm, model_name)
        self._plot_curves(fpr, tpr, roc_auc, recall_curve, precision_curve, pr_auc, model_name)
        self._plot_threshold_analysis(
            thresholds_curve,
            precision_curve[:-1], recall_curve[:-1], f1_curve[:-1],
            eval_threshold, model_name
        )
        self._plot_feature_importance(model, X_test.columns.tolist(), model_name)

        out_path = os.path.join(self.output_dir, "evaluation_report.json")
        with open(out_path, "w") as f:
            json.dump(self.evaluation_summary, f, indent=2)
        print(f"Evaluation report exported to {out_path}")
        return self.evaluation_summary

    def _plot_confusion_matrix(self, cm, model_name: str):
        plt.figure(figsize=(6, 5))
        sns.heatmap(cm, annot=True, fmt=",d", cmap="Blues", cbar=False,
                    xticklabels=['Predicted Legit (0)', 'Predicted Fraud (1)'],
                    yticklabels=['Actual Legit (0)', 'Actual Fraud (1)'])
        plt.title(f'Confusion Matrix - {model_name}', fontsize=12, fontweight='bold')
        plt.ylabel('Actual Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "eval_01_confusion_matrix.png"), dpi=300)
        plt.close()

    def _plot_curves(self, fpr, tpr, roc_auc, recall, precision, pr_auc, model_name: str):
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # ROC Curve
        axes[0].plot(fpr, tpr, color='#3b82f6', lw=2.5, label=f'ROC Curve (AUC = {roc_auc:.4f})')
        axes[0].plot([0, 1], [0, 1], color='gray', linestyle='--', label='Random Classifier')
        axes[0].set_xlim([0.0, 1.0])
        axes[0].set_ylim([0.0, 1.05])
        axes[0].set_xlabel('False Positive Rate (FPR)', fontsize=11)
        axes[0].set_ylabel('True Positive Rate (Recall)', fontsize=11)
        axes[0].set_title(f'ROC Curve - {model_name}', fontweight='bold')
        axes[0].legend(loc="lower right")
        axes[0].grid(True, alpha=0.3)

        # PR Curve
        axes[1].plot(recall, precision, color='#10b981', lw=2.5, label=f'PR Curve (PR-AUC = {pr_auc:.4f})')
        axes[1].set_xlim([0.0, 1.0])
        axes[1].set_ylim([0.0, 1.05])
        axes[1].set_xlabel('Recall (Fraud Detection Rate)', fontsize=11)
        axes[1].set_ylabel('Precision (Fraud Accuracy)', fontsize=11)
        axes[1].set_title(f'Precision-Recall Curve - {model_name}', fontweight='bold')
        axes[1].legend(loc="lower left")
        axes[1].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "eval_02_roc_pr_curves.png"), dpi=300)
        plt.close()

    def _plot_threshold_analysis(self, thresholds, precisions, recalls, f1_scores, best_thresh, model_name: str):
        plt.figure(figsize=(10, 5))
        plt.plot(thresholds, precisions, label='Precision (Accuracy of alerts)', color='#10b981', lw=2)
        plt.plot(thresholds, recalls, label='Recall (Caught frauds %)', color='#ef4444', lw=2)
        plt.plot(thresholds, f1_scores, label='F1-Score (Harmonic balance)', color='#3b82f6', lw=2.5, linestyle='--')
        plt.axvline(best_thresh, color='#8b5cf6', linestyle=':', lw=2, label=f'Optimal F1 Threshold ({best_thresh:.3f})')
        plt.xlabel('Decision Probability Threshold', fontsize=11)
        plt.ylabel('Score Metric', fontsize=11)
        plt.title(f'Threshold Operating Curve Optimization - {model_name}', fontsize=12, fontweight='bold')
        plt.legend(loc='best')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "eval_03_threshold_analysis.png"), dpi=300)
        plt.close()

    def _plot_feature_importance(self, model, feature_names: list, model_name: str):
        importances = None
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
        elif hasattr(model, "coef_"):
            importances = np.abs(model.coef_[0])

        if importances is not None:
            feat_imp = pd.Series(importances, index=feature_names).sort_values(ascending=False).head(15)
            plt.figure(figsize=(10, 6))
            sns.barplot(x=feat_imp.values, y=feat_imp.index, palette="viridis")
            plt.title(f'Top 15 Feature Importances - {model_name}', fontsize=12, fontweight='bold')
            plt.xlabel('Relative Importance Score')
            plt.tight_layout()
            plt.savefig(os.path.join(self.output_dir, "eval_04_feature_importance.png"), dpi=300)
            plt.close()

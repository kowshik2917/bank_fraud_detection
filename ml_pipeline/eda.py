"""
Module 1: Exploratory Data Analysis & Data Understanding
Intelligent Banking Fraud Detection Platform
Author: Senior Data Scientist
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns


class FraudDataExplorer:
    """Comprehensive Exploratory Data Analysis for Credit Card Transactions."""

    def __init__(self, data_path: str = "creditcard.csv", output_dir: str = "eda_outputs"):
        self.data_path = data_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.df = None
        self.summary_metrics = {}

    def load_data(self) -> pd.DataFrame:
        """Load dataset and record initial shape and memory footprint."""
        print("=" * 70)
        print(" MODULE 1: LOADING & DATASET UNDERSTANDING")
        print("=" * 70)
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Dataset not found at path: {self.data_path}")

        print(f"Loading dataset from: {self.data_path} ...")
        self.df = pd.read_csv(self.data_path)
        mem_usage_mb = self.df.memory_usage(deep=True).sum() / (1024 * 1024)
        
        self.summary_metrics["total_rows"] = int(self.df.shape[0])
        self.summary_metrics["total_columns"] = int(self.df.shape[1])
        self.summary_metrics["memory_mb"] = round(float(mem_usage_mb), 2)

        print(f"Dataset Loaded Successfully.")
        print(f"Rows: {self.df.shape[0]:,}, Columns: {self.df.shape[1]}")
        print(f"Memory Footprint: {mem_usage_mb:.2f} MB\n")
        return self.df

    def check_data_integrity(self) -> dict:
        """Inspect column types, null values, and duplicate records."""
        print("-" * 50)
        print("1. DATA INTEGRITY & MISSING VALUE AUDIT")
        print("-" * 50)
        null_counts = self.df.isnull().sum()
        total_nulls = int(null_counts.sum())
        num_duplicates = int(self.df.duplicated().sum())

        integrity = {
            "total_null_cells": total_nulls,
            "duplicate_records": num_duplicates,
            "duplicate_percentage": round((num_duplicates / len(self.df)) * 100, 3),
            "dtypes_distribution": {str(k): int(v) for k, v in self.df.dtypes.value_counts().items()}
        }
        self.summary_metrics["integrity"] = integrity

        print(f"Total Missing/Null Values: {total_nulls}")
        print(f"Duplicate Transactions: {num_duplicates} ({integrity['duplicate_percentage']}%)")
        print(f"Data Types Breakdown: {integrity['dtypes_distribution']}\n")
        return integrity

    def analyze_class_distribution(self) -> dict:
        """Examine severe class imbalance between legitimate and fraudulent transactions."""
        print("-" * 50)
        print("2. CLASS DISTRIBUTION & IMBALANCE RATIO")
        print("-" * 50)
        counts = self.df['Class'].value_counts()
        legit_count = int(counts.get(0, 0))
        fraud_count = int(counts.get(1, 0))
        total = legit_count + fraud_count
        fraud_pct = (fraud_count / total) * 100
        imbalance_ratio = legit_count / fraud_count if fraud_count > 0 else 0

        class_dist = {
            "legitimate_count": legit_count,
            "fraud_count": fraud_count,
            "fraud_percentage": round(fraud_pct, 4),
            "imbalance_ratio": f"{round(imbalance_ratio, 1)} : 1"
        }
        self.summary_metrics["class_distribution"] = class_dist

        print(f"Legitimate (Class 0): {legit_count:,} ({100 - fraud_pct:.3f}%)")
        print(f"Fraudulent (Class 1): {fraud_count:,} ({fraud_pct:.4f}%)")
        print(f"Imbalance Ratio: {class_dist['imbalance_ratio']} (Severe Imbalance)\n")

        # Visualization
        plt.figure(figsize=(7, 4.5))
        palette = ['#10b981', '#ef4444']
        ax = sns.barplot(x=['Legitimate (0)', 'Fraudulent (1)'], y=[legit_count, fraud_count], palette=palette)
        plt.yscale('log')
        plt.title('Transaction Class Distribution (Log Scale)', fontsize=13, fontweight='bold', pad=12)
        plt.ylabel('Count (Logarithmic Scale)')
        for p in ax.patches:
            height = p.get_height()
            ax.annotate(f'{int(height):,}\n({height/total*100:.2f}%)',
                        (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='bottom', fontsize=10, xytext=(0, 4),
                        textcoords='offset points')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "01_class_distribution.png"), dpi=300)
        plt.close()
        return class_dist

    def analyze_transaction_amounts(self) -> dict:
        """Statistical profile and distribution comparison of transaction amounts."""
        print("-" * 50)
        print("3. TRANSACTION AMOUNT STATISTICS & PROFILING")
        print("-" * 50)
        legit_amt = self.df[self.df['Class'] == 0]['Amount']
        fraud_amt = self.df[self.df['Class'] == 1]['Amount']

        amt_stats = {
            "legit_mean": round(float(legit_amt.mean()), 2),
            "legit_median": round(float(legit_amt.median()), 2),
            "legit_max": round(float(legit_amt.max()), 2),
            "legit_p95": round(float(legit_amt.quantile(0.95)), 2),
            "fraud_mean": round(float(fraud_amt.mean()), 2),
            "fraud_median": round(float(fraud_amt.median()), 2),
            "fraud_max": round(float(fraud_amt.max()), 2),
            "fraud_p95": round(float(fraud_amt.quantile(0.95)), 2)
        }
        self.summary_metrics["amount_statistics"] = amt_stats

        print(f"Legitimate Transactions - Mean: ${amt_stats['legit_mean']}, Median: ${amt_stats['legit_median']}, 95th Pct: ${amt_stats['legit_p95']}, Max: ${amt_stats['legit_max']}")
        print(f"Fraudulent Transactions - Mean: ${amt_stats['fraud_mean']}, Median: ${amt_stats['fraud_median']}, 95th Pct: ${amt_stats['fraud_p95']}, Max: ${amt_stats['fraud_max']}\n")

        # Visualization
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        sns.boxplot(x='Class', y='Amount', data=self.df, ax=axes[0], palette=['#10b981', '#ef4444'], showfliers=False)
        axes[0].set_xticklabels(['Legitimate (0)', 'Fraudulent (1)'])
        axes[0].set_title('Transaction Amount Boxplot (Excluding Extreme Outliers)', fontweight='bold')
        axes[0].set_ylabel('Amount ($)')

        sns.histplot(np.log1p(legit_amt), color='#10b981', label='Legitimate', kde=True, ax=axes[1], stat="density", bins=40, alpha=0.5)
        sns.histplot(np.log1p(fraud_amt), color='#ef4444', label='Fraudulent', kde=True, ax=axes[1], stat="density", bins=40, alpha=0.6)
        axes[1].set_title('Log-Transformed Amount Distribution log(1 + Amount)', fontweight='bold')
        axes[1].set_xlabel('log(Amount + 1)')
        axes[1].legend()

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "02_amount_distribution.png"), dpi=300)
        plt.close()
        return amt_stats

    def analyze_temporal_patterns(self):
        """Analyze transaction velocity across 48-hour cyclical timeline."""
        print("-" * 50)
        print("4. TEMPORAL FRAUD PATTERNS (CYCLICAL TIME ANALYSIS)")
        print("-" * 50)
        # Convert seconds from start of recording into 24-hour cycle
        self.df['Hour'] = ((self.df['Time'] / 3600) % 24).astype(int)

        hourly = self.df.groupby(['Hour', 'Class']).size().unstack(fill_value=0)
        hourly.columns = ['Legit', 'Fraud']
        hourly['Fraud_Rate_Pct'] = (hourly['Fraud'] / (hourly['Legit'] + hourly['Fraud'])) * 100

        print("Peak fraud rate hours (top 5):")
        print(hourly.sort_values(by='Fraud_Rate_Pct', ascending=False)[['Fraud', 'Legit', 'Fraud_Rate_Pct']].head(5))
        print()

        fig, ax1 = plt.subplots(figsize=(12, 5))
        color = '#3b82f6'
        ax1.set_xlabel('Hour of Day (0 - 23)', fontsize=11)
        ax1.set_ylabel('Total Legitimate Volume', color=color, fontsize=11)
        ax1.plot(hourly.index, hourly['Legit'], color=color, marker='o', linewidth=2, label='Legitimate Volume')
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.grid(True, linestyle='--', alpha=0.4)

        ax2 = ax1.twinx()
        color = '#ef4444'
        ax2.set_ylabel('Fraud Rate (%)', color=color, fontsize=11)
        ax2.plot(hourly.index, hourly['Fraud_Rate_Pct'], color=color, marker='s', linewidth=2.5, linestyle='--', label='Fraud Rate %')
        ax2.tick_params(axis='y', labelcolor=color)

        plt.title('Transaction Volume vs. Fraud Rate by Hour of Day', fontsize=13, fontweight='bold')
        fig.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "03_temporal_patterns.png"), dpi=300)
        plt.close()

    def analyze_correlations_and_features(self):
        """Compute correlations with Class and identify most predictive PCA components."""
        print("-" * 50)
        print("5. FEATURE CORRELATION & PREDICTIVE SIGNAL DISCOVERY")
        print("-" * 50)
        corrs = self.df.corr()['Class'].drop(['Class', 'Hour'] if 'Hour' in self.df.columns else ['Class'])
        sorted_corrs = corrs.sort_values()

        top_negative = sorted_corrs.head(5)
        top_positive = sorted_corrs.tail(5)

        print("Top Negative Correlations with Fraud (Lower values -> Higher Fraud Risk):")
        for feat, val in top_negative.items():
            print(f"  {feat}: {val:+.4f}")

        print("\nTop Positive Correlations with Fraud (Higher values -> Higher Fraud Risk):")
        for feat, val in top_positive.items():
            print(f"  {feat}: {val:+.4f}")
        print()

        # Correlation Barplot
        plt.figure(figsize=(12, 6))
        colors = ['#ef4444' if x > 0 else '#3b82f6' for x in sorted_corrs.values]
        sorted_corrs.plot(kind='bar', color=colors, width=0.8)
        plt.title('Feature Correlation with Fraud Target (Class)', fontsize=13, fontweight='bold')
        plt.ylabel('Pearson Correlation Coefficient')
        plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "04_feature_correlations.png"), dpi=300)
        plt.close()

        # Heatmap of top 10 most correlated features
        top_feats = list(top_negative.index) + list(top_positive.index) + ['Amount', 'Class']
        plt.figure(figsize=(10, 8))
        sns.heatmap(self.df[top_feats].corr(), annot=True, fmt=".2f", cmap='coolwarm', vmin=-1, vmax=1, linewidths=0.5)
        plt.title('Correlation Matrix of Top Predictive Features', fontsize=13, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "05_correlation_heatmap.png"), dpi=300)
        plt.close()

    def generate_eda_report(self) -> str:
        """Synthesize all EDA insights into a structured executive report."""
        report_path = os.path.join(self.output_dir, "eda_summary_report.json")
        with open(report_path, "w") as f:
            json.dump(self.summary_metrics, f, indent=2)
        print(f"EDA Summary Metrics exported to {report_path}")
        print("=" * 70)
        print(" MODULE 1: EDA COMPLETE - ALL VISUALIZATIONS GENERATED")
        print("=" * 70)
        return report_path

    def run_full_eda(self):
        """Execute complete EDA lifecycle."""
        self.load_data()
        self.check_data_integrity()
        self.analyze_class_distribution()
        self.analyze_transaction_amounts()
        self.analyze_temporal_patterns()
        self.analyze_correlations_and_features()
        self.generate_eda_report()


if __name__ == "__main__":
    explorer = FraudDataExplorer()
    explorer.run_full_eda()

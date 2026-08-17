"""
Master ML Training & Orchestration Pipeline
Intelligent Banking Fraud Detection Platform
Executes Modules 1 through 9 and Module 13 end-to-end.
"""

import os
import sys
import json
import time
import pandas as pd
from datetime import datetime

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath("."))

from ml_pipeline.eda import FraudDataExplorer
from ml_pipeline.preprocessing import FraudDataPreprocessor
from ml_pipeline.feature_engineering import FraudFeatureEngineer
from ml_pipeline.imbalance_handler import ImbalanceHandler
from ml_pipeline.model_training import FraudModelTrainer
from ml_pipeline.model_evaluation import FraudModelEvaluator
from ml_pipeline.explainability import FraudShapExplainer
from ml_pipeline.anomaly_detection import AnomalyDetectionEngine
from ml_pipeline.risk_engine import RiskScoringEngine
from ml_pipeline.pdf_generator import FraudReportGenerator


def run_full_fraud_pipeline():
    start_time = time.time()
    print("=" * 85)
    print(" STARTING MASTER BANKING FRAUD ML & ANALYTICS PIPELINE")
    print(f" Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 85)

    os.makedirs("models", exist_ok=True)
    os.makedirs("eda_outputs", exist_ok=True)
    os.makedirs("evaluation_outputs", exist_ok=True)
    os.makedirs("shap_outputs", exist_ok=True)
    os.makedirs("reports_output", exist_ok=True)

    # ----------------------------------------------------
    # Module 1: Exploratory Data Analysis
    # ----------------------------------------------------
    print("\n>>> [STEP 1/10] Running Exploratory Data Analysis...")
    eda_explorer = FraudDataExplorer(data_path="creditcard.csv", output_dir="eda_outputs")
    eda_explorer.run_full_eda()

    # ----------------------------------------------------
    # Module 2: Data Preprocessing
    # ----------------------------------------------------
    print("\n>>> [STEP 2/10] Building Production Preprocessing Pipeline...")
    raw_df = pd.read_csv("creditcard.csv")
    preprocessor = FraudDataPreprocessor(models_dir="models")
    
    clean_df = preprocessor.clean_raw_data(raw_df, drop_duplicates=True)
    X_train, X_test, y_train, y_test = preprocessor.prepare_train_test_split(clean_df, test_size=0.2)
    
    # Fit & transform with Winsorization & Scalers
    preprocessor.fit(X_train)
    X_train_clean = preprocessor.transform(X_train)
    X_test_clean = preprocessor.transform(X_test)
    preprocessor.save_pipeline()

    # ----------------------------------------------------
    # Module 3: Advanced Feature Engineering
    # ----------------------------------------------------
    print("\n>>> [STEP 3/10] Engineering Advanced Behavioral & Temporal Features...")
    feature_engineer = FraudFeatureEngineer(models_dir="models")
    X_train_feat = feature_engineer.fit_transform(X_train_clean)
    X_test_feat = feature_engineer.transform(X_test_clean)
    feature_engineer.save()
    print(f"Total Feature Count after Engineering: {X_train_feat.shape[1]}")

    # ----------------------------------------------------
    # Module 4: Imbalanced Data Handling Analysis
    # ----------------------------------------------------
    print("\n>>> [STEP 4/10] Evaluating Imbalanced Resampling Strategies...")
    imbalance_mgr = ImbalanceHandler()
    imbalance_comparison = imbalance_mgr.compare_resampling_strategies(X_train_feat, y_train)

    # ----------------------------------------------------
    # Module 5: Supervised Fraud Model Training & Benchmark
    # ----------------------------------------------------
    print("\n>>> [STEP 5/10] Training & Benchmarking Classification Models...")
    trainer = FraudModelTrainer(models_dir="models")
    benchmark_df = trainer.train_and_benchmark(X_train_feat, y_train, X_test_feat, y_test)
    trainer.save_best_model()

    # ----------------------------------------------------
    # Module 6: Model Evaluation & Diagnostic Curves
    # ----------------------------------------------------
    print("\n>>> [STEP 6/10] Executing Diagnostic Model Evaluation...")
    evaluator = FraudModelEvaluator(output_dir="evaluation_outputs")
    eval_report = evaluator.evaluate_model(
        trainer.best_model,
        trainer.best_model_name,
        X_test_feat,
        y_test
    )

    # ----------------------------------------------------
    # Module 7: SHAP Explainability Integration
    # ----------------------------------------------------
    print("\n>>> [STEP 7/10] Fitting SHAP Explainability Engine...")
    shap_engine = FraudShapExplainer(models_dir="models", output_dir="shap_outputs")
    shap_engine.fit_explainer(trainer.best_model, X_train_feat)
    # Generate global summary plots on test subset
    test_sample = X_test_feat.sample(min(300, len(X_test_feat)), random_state=42)
    shap_engine.generate_summary_plots(test_sample)
    
    # Generate sample waterfall plot on a high risk transaction
    fraud_indices = y_test[y_test == 1].index
    if len(fraud_indices) > 0:
        sample_fraud_row = X_test_feat.loc[fraud_indices[0]]
        shap_engine.generate_waterfall_plot(sample_fraud_row)
    shap_engine.save()

    # ----------------------------------------------------
    # Module 8: Unsupervised Anomaly Detection (Isolation Forest / LOF)
    # ----------------------------------------------------
    print("\n>>> [STEP 8/10] Training Unsupervised Anomaly Detection Engine...")
    anomaly_engine = AnomalyDetectionEngine(models_dir="models", contamination=0.002)
    # Fit anomaly models on legitimate training records
    X_train_normal = X_train_feat[y_train == 0]
    anomaly_engine.fit(X_train_normal)
    anomaly_engine.save()

    # ----------------------------------------------------
    # Module 9: Risk Scoring Engine Verification
    # ----------------------------------------------------
    print("\n>>> [STEP 9/10] Initializing Calibrated Risk Scoring Engine...")
    risk_engine = RiskScoringEngine()
    test_risk = risk_engine.calculate_risk_score(
        fraud_probability=0.94,
        anomaly_score=87.5,
        transaction_amount=2450.0,
        is_night=True,
        extreme_feature_count=4
    )
    print("Risk Engine Calibrated Test Case:", test_risk)

    # ----------------------------------------------------
    # Module 13: Test PDF Forensic Dossier Generation
    # ----------------------------------------------------
    print("\n>>> [STEP 10/10] Generating Sample Forensic PDF Report Dossier...")
    pdf_gen = FraudReportGenerator(output_dir="reports_output")
    sample_pdf = pdf_gen.generate_pdf_report(
        case_id="CASE-2026-INIT",
        transaction_data={"transaction_id": "TXN-INIT-001", "amount": 2450.0, "timestamp": "2026-08-16 20:20:00 UTC"},
        risk_data=test_risk,
        shap_data=shap_engine.explain_transaction(sample_fraud_row if len(fraud_indices) > 0 else X_test_feat.iloc[0]),
        investigator_notes="System automated pipeline validation dossier. Verified all models operational."
    )

    # Save Pipeline Global Metadata
    metadata = {
        "build_timestamp": datetime.utcnow().isoformat(),
        "total_training_samples": len(X_train_feat),
        "total_test_samples": len(X_test_feat),
        "feature_names": X_train_feat.columns.tolist(),
        "best_model_name": trainer.best_model_name,
        "benchmark_summary": benchmark_df.to_dict(orient="records"),
        "evaluation_summary": eval_report,
        "imbalance_comparison": imbalance_comparison,
        "eda_summary": eda_explorer.summary_metrics,
        "sample_pdf_report": sample_pdf,
        "pipeline_status": "READY"
    }

    metadata_path = os.path.join("models", "pipeline_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    total_time = round(time.time() - start_time, 2)
    print("\n" + "=" * 85)
    print(f" PIPELINE COMPLETED SUCCESSFULLY IN {total_time} SECONDS")
    print(f" Metadata & Model Artifacts saved to 'models/'")
    print("=" * 85)


if __name__ == "__main__":
    run_full_fraud_pipeline()

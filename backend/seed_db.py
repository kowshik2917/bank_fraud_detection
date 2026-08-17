"""
Database Seeder Script
Populates MongoDB / Local Storage with initial fraud and legitimate records,
active triage alerts, and historical investigation reports.
"""

import os
import sys

sys.path.insert(0, os.path.abspath("."))

import uuid
import random
import pandas as pd
from datetime import datetime, timedelta
from backend.database import db_instance


def seed_platform_database(num_records: int = 150):
    print("=" * 60)
    print(" SEEDING FRAUD PLATFORM DATABASE")
    print("=" * 60)

    if not os.path.exists("creditcard.csv"):
        print("[Seeder] creditcard.csv not found, skipping CSV sampling.")
        return

    df = pd.read_csv("creditcard.csv")
    fraud_df = df[df['Class'] == 1]
    legit_df = df[df['Class'] == 0]

    # Sample 30 fraud and 120 legit transactions
    n_fraud = min(30, len(fraud_df))
    n_legit = min(num_records - n_fraud, len(legit_df))

    sampled_fraud = fraud_df.sample(n_fraud, random_state=42)
    sampled_legit = legit_df.sample(n_legit, random_state=42)
    combined = pd.concat([sampled_fraud, sampled_legit]).sample(frac=1.0, random_state=42).reset_index(drop=True)

    now = datetime.utcnow()
    merchants = ["Amazon US", "Apple Store NYC", "QuickPay Wire Transfer", "Shell Gas Station", "Luxury Boutique Paris", "Steam Games", "CryptoExchange Pro", "Uber Rides", "Target Supercenter", "Walmart Online"]
    statuses = ["OPEN", "INVESTIGATING", "CONFIRMED_FRAUD", "FALSE_POSITIVE", "RESOLVED"]

    inserted_txns = 0
    inserted_alerts = 0

    for idx, row in combined.iterrows():
        is_fraud = int(row['Class']) == 1
        delta_mins = random.randint(5, 2880)
        txn_time = (now - timedelta(minutes=delta_mins)).isoformat()
        amt = round(float(row['Amount']), 2)
        txn_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        cust_id = f"CUST-{random.randint(10000, 99999)}"

        if is_fraud:
            risk_score = round(random.uniform(75.0, 98.5), 1)
            risk_lvl = "CRITICAL" if risk_score >= 85 else "HIGH"
            fraud_prob = round(random.uniform(0.78, 0.99), 4)
            anomaly_score = round(random.uniform(70.0, 95.0), 1)
            action = "AUTO_BLOCK" if risk_lvl == "CRITICAL" else "MANUAL_INVESTIGATION"
        else:
            # Mostly low, occasional medium
            is_med = random.random() < 0.08
            if is_med:
                risk_score = round(random.uniform(32.0, 58.0), 1)
                risk_lvl = "MEDIUM"
                fraud_prob = round(random.uniform(0.20, 0.45), 4)
                anomaly_score = round(random.uniform(30.0, 55.0), 1)
                action = "STEP_UP_AUTH"
            else:
                risk_score = round(random.uniform(2.0, 24.0), 1)
                risk_lvl = "LOW"
                fraud_prob = round(random.uniform(0.001, 0.08), 4)
                anomaly_score = round(random.uniform(5.0, 25.0), 1)
                action = "APPROVE"

        record = {
            "transaction_id": txn_id,
            "cardholder_id": cust_id,
            "merchant_name": random.choice(merchants),
            "amount": amt,
            "time": float(row['Time']),
            "fraud_probability": fraud_prob,
            "anomaly_score": anomaly_score,
            "final_risk_score": risk_score,
            "risk_level": risk_lvl,
            "action": action,
            "timestamp": txn_time,
            "features": {c: round(float(row[c]), 4) for c in df.columns if c.startswith('V')}
        }
        db_instance.insert_transaction(record)
        inserted_txns += 1

        # Generate alert if high or critical
        if risk_lvl in ["HIGH", "CRITICAL"]:
            alert_id = f"ALT-{uuid.uuid4().hex[:6].upper()}"
            alert = {
                "alert_id": alert_id,
                "transaction_id": txn_id,
                "cardholder_id": cust_id,
                "amount": amt,
                "fraud_probability": fraud_prob,
                "risk_score": risk_score,
                "risk_level": risk_lvl,
                "status": random.choice(statuses),
                "triggered_rules": ["Elevated PCA deviation (V14/V12)", "Unusual velocity proxy"] if is_fraud else ["Off-hours transaction"],
                "reason_codes": [
                    f"Latent component deviation (V14 = {row['V14']:.2f})",
                    f"Spending deviation from baseline (${amt:,.2f})"
                ],
                "created_at": txn_time,
                "last_reviewed_by": "Lead Fraud Analyst #8142"
            }
            db_instance.insert_alert(alert)
            inserted_alerts += 1

    print(f"[Seeder] Inserted {inserted_txns} Transactions and {inserted_alerts} Alerts successfully.")
    print("=" * 60)


if __name__ == "__main__":
    seed_platform_database()

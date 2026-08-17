# Sentinel: Banking Fraud Detection & Investigation Platform

![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python%203.11-009688?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/Frontend-React%2018%20%7C%20Vite-61DAFB?style=for-the-badge&logo=react)
![XGBoost](https://img.shields.io/badge/ML%20Engine-XGBoost%20%7C%20CatBoost%20%7C%20SHAP-FF6F00?style=for-the-badge)
![MongoDB](https://img.shields.io/badge/Database-MongoDB%204.6-47A248?style=for-the-badge&logo=mongodb)

A real-time Banking Fraud Detection, Explainable AI, Threat Triage, and Forensic PDF Investigation platform built on the [Credit Card Fraud Detection dataset](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) (284,807 transactions).

---

## 🏛️ Architecture Overview

| Module | Core Responsibility | Artifact |
|---|---|---|
| **EDA** | Class skew, Tukey outlier detection, PCA correlations, temporal cycles | `ml_pipeline/eda.py` |
| **Preprocessing** | Winsorization (IQR), Robust scaling, Stratified 60/20/20 split | `ml_pipeline/preprocessing.py` |
| **Feature Engineering** | Cyclical time harmonics, log-Amount, PCA extreme counts, inter-transaction gap | `ml_pipeline/feature_engineering.py` |
| **Imbalance Handling** | SMOTE, ADASYN, cost-sensitive `scale_pos_weight` benchmark | `ml_pipeline/imbalance_handler.py` |
| **Model Training** | Logistic Regression, Random Forest, XGBoost, CatBoost; validation-tuned threshold | `ml_pipeline/model_training.py` |
| **Model Evaluation** | Confusion matrix, PR-AUC, ROC-AUC, threshold curves at validation-selected threshold | `ml_pipeline/model_evaluation.py` |
| **Explainable AI (SHAP)** | TreeExplainer attribution, waterfall, beeswarm, automated reason codes | `ml_pipeline/explainability.py` |
| **Anomaly Detection** | Isolation Forest + LOF normalized outlier scoring | `ml_pipeline/anomaly_detection.py` |
| **Risk Scoring Engine** | Calibrated 0–100 composite score (Supervised + Anomaly + Heuristics) | `ml_pipeline/risk_engine.py` |
| **MongoDB** | Collections: `transactions`, `alerts`, `users`, `reports`, `search_logs` | `backend/database.py` |
| **FastAPI Backend** | Endpoints: `/predict`, `/transactions`, `/alerts`, `/dashboard`, `/reports`, `/auth` | `backend/` |
| **React Dashboard** | 6 pages: Dashboard, Transaction Explorer, Fraud Analytics, SHAP, Alerts Center, Reports | `frontend/` |
| **PDF Dossiers** | ReportLab forensic PDFs with risk breakdown, SHAP drivers, and SHA-256 audit hash | `ml_pipeline/pdf_generator.py` |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB running locally on `mongodb://127.0.0.1:27017`
- `creditcard.csv` downloaded from [Kaggle](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) and placed in the project root (**not committed to git — too large**)

### 1. Backend Setup

```bash
# Install Python dependencies (includes bcrypt, passlib, FastAPI, XGBoost, etc.)
pip install -r backend/requirements.txt

# (Optional) Re-train all ML models from scratch — requires creditcard.csv
python ml_pipeline/run_pipeline.py

# Start FastAPI server on port 8005
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8005 --reload
```

API docs: **`http://localhost:8005/docs`**

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Dashboard: **`http://localhost:3000`**

### 3. MongoDB

The backend connects to `mongodb://127.0.0.1:27017` by default (database: `fraud_platform_db`).
To use MongoDB Atlas, set `MONGODB_URI` in a `.env` file (see `deployment/.env.example`).

---

## 📊 Risk Scoring Formula

$$\text{Final Risk Score} = 100 \times \left( 0.65 \times P_{\text{XGBoost}} + 0.25 \times \frac{S_{\text{IsoForest}}}{100} + 0.10 \times \frac{S_{\text{Heuristics}}}{100} \right)$$

| Tier | Score | Action |
|---|---|---|
| **LOW** | 0 – 29.9 | Frictionless auto-approval |
| **MEDIUM** | 30 – 59.9 | Step-up authentication (2FA / Biometric) |
| **HIGH** | 60 – 84.9 | Hold for fraud analyst queue review |
| **CRITICAL** | 85 – 100 | Immediate block & card lock |

---

## 🔬 ML Methodology

### Train / Validation / Test Split (60 / 20 / 20)

The dataset is split into three disjoint stratified folds:

- **Train (60%)** — all model parameters fitted here.
- **Validation (20%)** — decision threshold tuned by F1 maximisation; model selection by PR-AUC. The test set is **never seen** during this phase.
- **Test (20%)** — final held-out evaluation only, at the validation-tuned threshold. Prevents look-ahead bias in reported metrics.

### Validation-Based Threshold Selection

Each model's optimal decision threshold is found on the validation set (not test), then applied at inference time. The threshold is saved inside `models/best_fraud_model.pkl`.

### Feature Engineering

| Feature | Description |
|---|---|
| `Hour`, `Sin_Hour`, `Cos_Hour` | Cyclical time-of-day encoding |
| `Is_Night_Transaction` | Flag for 23:00–06:00 window |
| `Amount_Log`, `Amount_Tier`, `Amount_Deviation_Z` | Spend profiling |
| `V_Extreme_Count` | PCA components exceeding ±3σ |
| `Risk_Indicator_Index` | Weighted composite of top fraud-correlated PCA features |
| `Time_Since_Prev_Global` | log1p inter-transaction gap (globally sorted) |

> **Note on velocity features**: True per-cardholder transaction velocity (e.g., "3 txns in 10 min for card X") is not computable from this dataset because the public `creditcard.csv` contains no cardholder identifier — all features V1–V28 are PCA-transformed for anonymisation. The former `Velocity_Proxy` was removed as it was row-order dependent and had no real meaning.

---

## 🔒 Security

- **Passwords** are hashed with **bcrypt** (salted, adaptive cost via `passlib`). SHA-256 is not used.
- **Transparent migration**: existing accounts with legacy SHA-256 hashes are silently re-hashed to bcrypt on next successful login.
- Each analyst's workspace is isolated by `X-User-Email` header — transactions, alerts, and reports are user-scoped.
- Password hashes are never returned by any API endpoint.

---

## ⚠️ Known Limitations

| Limitation | Detail |
|---|---|
| Per-cardholder velocity | Not available — no cardholder ID in PCA-anonymised dataset |
| `creditcard.csv` not in repo | 143 MB; download from Kaggle separately |
| `models/anomaly_engine.pkl` not in repo | 83 MB; regenerate with `python ml_pipeline/run_pipeline.py` |
| No real-time WebSocket push | Dashboard polls every 30 s; WebSocket support planned |

---

## 🌐 Cloud Deployment (Non-Docker)

### Backend on Render

1. Push this repo to GitHub (without `creditcard.csv` or large `.pkl` files).
2. Create a **Web Service** in Render pointing to the repo.
3. Set Build Command: `pip install -r backend/requirements.txt`
4. Set Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. Add env var: `MONGODB_URI` = your MongoDB Atlas connection string.

### Frontend on Vercel

1. Import the GitHub repo in Vercel.
2. Root Directory: `frontend` | Framework: `Vite`
3. Build Command: `npm run build` | Output: `dist`
4. Add env var: `VITE_API_URL` = your Render backend URL.

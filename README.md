# Sentinel: Intelligent Banking Fraud Detection & Investigation Platform

![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python%203.11-009688?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/Frontend-React%2018%20%7C%20Vite%20%7C%20Tailwind-61DAFB?style=for-the-badge&logo=react)
![XGBoost](https://img.shields.io/badge/ML%20Engine-XGBoost%20%7C%20CatBoost%20%7C%20SHAP-FF6F00?style=for-the-badge)
![Security](https://img.shields.io/badge/Security-PCI--DSS%20Compliant%20Audit-10B981?style=for-the-badge)

An enterprise-grade, real-time Banking Fraud Detection, Explainable AI, Threat Triage, and Forensic PDF Investigation platform built on the Credit Card Fraud Detection dataset (284,807 transactions).

---

## 🏛️ Comprehensive 14-Module Architecture

| Module | Role | Core Responsibility | Artifact / Code |
|---|---|---|---|
| **Module 1: EDA & Data Understanding** | Senior Data Scientist | Comprehensive class skew, Tukey outlier detection, PCA correlations, temporal 48h cycles | `ml_pipeline/eda.py` |
| **Module 2: Data Preprocessing** | ML Engineer | Production Winsorization (IQR capping), Robust scaling, Stratified 80/20 splitting | `ml_pipeline/preprocessing.py` |
| **Module 3: Feature Engineering** | Fraud Analytics Engineer | Cyclical hour harmonics, $\log_{1p}(\text{Amount})$ deviations, PCA extreme indices, velocity proxy | `ml_pipeline/feature_engineering.py` |
| **Module 4: Imbalanced Data Handling** | Fraud ML Specialist | SMOTE, ADASYN, cost-sensitive `scale_pos_weight` benchmark evaluations | `ml_pipeline/imbalance_handler.py` |
| **Module 5: Fraud Detection Models** | Senior ML Engineer | Logistic Regression, Random Forest, CatBoost, and XGBoost training & model selection | `ml_pipeline/model_training.py` |
| **Module 6: Model Evaluation** | AI Evaluation Specialist | Confusion matrices, PR-AUC curves, ROC-AUC, threshold optimization curves, feature importances | `ml_pipeline/model_evaluation.py` |
| **Module 7: Explainable AI (SHAP)** | Explainable AI Expert | TreeExplainer attribution, waterfall diagrams, beeswarm plots, automated human reason codes | `ml_pipeline/explainability.py` |
| **Module 8: Anomaly Detection** | Fraud Specialist | Unsupervised Isolation Forest and Local Outlier Factor (LOF) normalized outlier scoring | `ml_pipeline/anomaly_detection.py` |
| **Module 9: Risk Scoring Engine** | Risk Analytics Engineer | Calibrated 0–100 multi-factor risk score (Supervised + Anomaly + Heuristic rules) with Low/Med/High/Critical tiers | `ml_pipeline/risk_engine.py` |
| **Module 10: MongoDB Integration** | Backend Engineer | Collections (`transactions`, `alerts`, `investigations`, `reports`) with resilient local fallback | `backend/database.py` |
| **Module 11: FastAPI Production Backend** | Senior Backend Engineer | Endpoints (`/predict`, `/batch-predict`, `/anomaly`, `/transactions`, `/alerts`, `/dashboard`, `/reports`) | `backend/` |
| **Module 12: React Investigation Dashboard** | Senior Frontend Engineer | 6 pages: Dashboard Overview, Explorer, Fraud Analytics, SHAP, Alerts Center, Reports Page | `frontend/` |
| **Module 13: Forensic PDF Dossiers** | Reporting Engineer | ReportLab audit-ready PDF dossiers with transaction data, risk breakdown, SHAP drivers, and SHA-256 hash | `ml_pipeline/pdf_generator.py` |
| **Module 14: Cloud Deployment** | DevOps Engineer | Native FastAPI on Render, React Vite on Vercel, MongoDB Atlas database | `deployment/` |

---

## 🚀 Quick Start (Local Run)

### 1. Backend & ML Execution

```bash
# 1. Install Python dependencies
pip install -r backend/requirements.txt

# 2. Run end-to-end ML Training & Artifact Serialization
python ml_pipeline/run_pipeline.py

# 3. Seed Database with sample transactions and active alerts
python backend/seed_db.py

# 4. Start FastAPI Production Server
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation is live at: **`http://localhost:8000/docs`**

### 2. Frontend React Dashboard

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install Node dependencies
npm install

# 3. Launch Development Server
npm run dev
```
Dashboard is live at: **`http://localhost:3000`**

---

## 📊 Calibrated Multi-Factor Risk Scoring Formula

$$\text{Final Risk Score} = 100 \times \left( 0.65 \times P_{\text{XGBoost}} + 0.25 \times \frac{S_{\text{IsoForest}}}{100} + 0.10 \times \frac{S_{\text{Heuristics}}}{100} \right)$$

### Operational Decision Tiers:
- **`LOW` (0.0 – 29.9)**: Frictionless Auto-Approval
- **`MEDIUM` (30.0 – 59.9)**: Step-Up Authentication (2FA / Biometric Challenge)
- **`HIGH` (60.0 – 84.9)**: Hold for Fraud Analyst Queue Review
- **`CRITICAL` (85.0 – 100.0)**: Immediate Auto-Termination & Card Lock

---

## 🌐 Production Cloud Deployment Guide (Non-Docker)

### Deploy Backend on Render:
1. Push this repository to your GitHub.
2. In Render dashboard, create a new **Web Service** pointing to your repo.
3. Configure settings:
   - **Runtime**: Python 3.11
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. Set Environment Variables:
   - `MONGODB_URI`: `<your-mongodb-atlas-connection-string>`

### Deploy Frontend on Vercel:
1. In Vercel dashboard, import your GitHub repository.
2. Configure settings:
   - **Root Directory**: `frontend`
   - **Framework Preset**: `Vite`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
3. In Environment Variables, set:
   - `VITE_API_URL`: `https://your-backend-service.onrender.com`
4. Click **Deploy**.

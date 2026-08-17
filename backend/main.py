"""
Main FastAPI Application Entrypoint
Intelligent Banking Fraud Detection Platform
Author: Senior Backend Engineer
"""

import os
import sys

sys.path.insert(0, os.path.abspath("."))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.routes.predict import router as predict_router
from backend.routes.anomaly import router as anomaly_router
from backend.routes.transactions import router as transactions_router
from backend.routes.alerts import router as alerts_router
from backend.routes.dashboard import router as dashboard_router
from backend.routes.reports import router as reports_router
from backend.database import db_instance

app = FastAPI(
    title="Sentinel Intelligent Banking Fraud Detection API",
    description="Enterprise Real-Time ML Fraud Detection, SHAP Explainability & Forensic Investigation Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for Frontend React App
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include All Routers
app.include_router(predict_router)
app.include_router(anomaly_router)
app.include_router(transactions_router)
app.include_router(alerts_router)
app.include_router(dashboard_router)
app.include_router(reports_router)

# Mount static directories if available
os.makedirs("reports_output", exist_ok=True)
os.makedirs("shap_outputs", exist_ok=True)
os.makedirs("eda_outputs", exist_ok=True)
os.makedirs("evaluation_outputs", exist_ok=True)

app.mount("/static/reports", StaticFiles(directory="reports_output"), name="reports_static")
app.mount("/static/shap", StaticFiles(directory="shap_outputs"), name="shap_static")
app.mount("/static/eda", StaticFiles(directory="eda_outputs"), name="eda_static")
app.mount("/static/eval", StaticFiles(directory="evaluation_outputs"), name="eval_static")


@app.get("/", tags=["Health & Status"])
def root_status():
    return {
        "platform": "Sentinel Intelligent Banking Fraud Detection Platform",
        "version": "1.0.0",
        "status": "OPERATIONAL",
        "database": "MongoDB Atlas" if db_instance.is_connected else "Resilient In-Memory & Local Storage",
        "api_docs": "/docs"
    }


@app.get("/health", tags=["Health & Status"])
def health_check():
    return {
        "status": "HEALTHY",
        "database_connected": db_instance.is_connected
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

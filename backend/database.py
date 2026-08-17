"""
Module 10: MongoDB Atlas Integration & Resilient Storage Layer
Intelligent Banking Fraud Detection Platform
Author: Senior Backend Engineer
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False


class DatabaseManager:
    """
    Unified MongoDB Atlas connection manager with resilient in-memory/JSON storage fallback.
    Collections managed:
    - transactions
    - alerts
    - investigations
    - reports
    """

    def __init__(self, uri: Optional[str] = None, db_name: str = "fraud_platform_db"):
        self.uri = uri or os.getenv("MONGODB_URI")
        self.db_name = db_name
        self.client = None
        self.db = None
        self.is_connected = False
        
        # Local in-memory store for fallback
        self._local_storage = {
            "transactions": [],
            "alerts": [],
            "investigations": [],
            "reports": []
        }
        self._init_connection()

    def _init_connection(self):
        """Attempt connection to MongoDB Atlas."""
        if self.uri and PYMONGO_AVAILABLE:
            try:
                print(f"[MongoDB] Connecting to MongoDB Atlas...")
                self.client = MongoClient(self.uri, serverSelectionTimeoutMS=3000)
                # Verify connection
                self.client.admin.command('ping')
                self.db = self.client[self.db_name]
                self.is_connected = True
                print(f"[MongoDB] Connected successfully to Atlas database '{self.db_name}'")
                self._setup_indexes()
                return
            except (ConnectionFailure, ServerSelectionTimeoutError, Exception) as e:
                print(f"[MongoDB] Connection failed ({e}). Falling back to Resilient Local Store.")
        else:
            print("[MongoDB] No MONGODB_URI provided. Initialized Resilient In-Memory & Local Database.")
        
        self.is_connected = False

    def _setup_indexes(self):
        """Create high-performance indexes in MongoDB Atlas."""
        try:
            self.db.transactions.create_index("transaction_id", unique=True)
            self.db.transactions.create_index("timestamp")
            self.db.transactions.create_index("risk_level")
            self.db.alerts.create_index("alert_id", unique=True)
            self.db.alerts.create_index("status")
            self.db.reports.create_index("case_id", unique=True)
        except Exception as e:
            print(f"[MongoDB] Index creation note: {e}")

    # ----------------------------------------------------
    # Transaction Operations
    # ----------------------------------------------------
    def insert_transaction(self, record: Dict[str, Any]) -> str:
        """Insert transaction log with fraud prediction payload."""
        if not record.get("transaction_id"):
            record["transaction_id"] = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        if not record.get("timestamp"):
            record["timestamp"] = datetime.utcnow().isoformat()

        if self.is_connected:
            self.db.transactions.insert_one(record)
        else:
            self._local_storage["transactions"].insert(0, record)
        return record["transaction_id"]

    def get_transactions(
        self,
        limit: int = 50,
        skip: int = 0,
        risk_level: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve paginated transactions with filter support."""
        if self.is_connected:
            query = {}
            if risk_level and risk_level.upper() != "ALL":
                query["risk_level"] = risk_level.upper()
            if search:
                query["$or"] = [
                    {"transaction_id": {"$regex": search, "$options": "i"}},
                    {"cardholder_id": {"$regex": search, "$options": "i"}}
                ]
            cursor = self.db.transactions.find(query, {"_id": 0}).sort("timestamp", -1).skip(skip).limit(limit)
            return list(cursor)
        else:
            records = self._local_storage["transactions"]
            if risk_level and risk_level.upper() != "ALL":
                records = [r for r in records if r.get("risk_level", "").upper() == risk_level.upper()]
            if search:
                s = search.lower()
                records = [r for r in records if s in r.get("transaction_id", "").lower() or s in r.get("cardholder_id", "").lower()]
            return records[skip : skip + limit]

    # ----------------------------------------------------
    # Alert Operations
    # ----------------------------------------------------
    def insert_alert(self, alert_data: Dict[str, Any]) -> str:
        """Create fraud investigation alert."""
        if not alert_data.get("alert_id"):
            alert_data["alert_id"] = f"ALT-{uuid.uuid4().hex[:6].upper()}"
        if not alert_data.get("created_at"):
            alert_data["created_at"] = datetime.utcnow().isoformat()
        if not alert_data.get("status"):
            alert_data["status"] = "OPEN"

        if self.is_connected:
            self.db.alerts.insert_one(alert_data)
        else:
            self._local_storage["alerts"].insert(0, alert_data)
        return alert_data["alert_id"]

    def get_alerts(self, status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get active alert queue."""
        if self.is_connected:
            query = {}
            if status and status.upper() != "ALL":
                query["status"] = status.upper()
            cursor = self.db.alerts.find(query, {"_id": 0}).sort("created_at", -1).limit(limit)
            return list(cursor)
        else:
            alerts = self._local_storage["alerts"]
            if status and status.upper() != "ALL":
                alerts = [a for a in alerts if a.get("status", "").upper() == status.upper()]
            return alerts[:limit]

    def update_alert_status(
        self,
        alert_id: str,
        new_status: str,
        notes: Optional[str] = None,
        analyst_name: str = "Lead Fraud Analyst"
    ) -> bool:
        """Update triage status for an alert."""
        update_doc = {
            "status": new_status,
            "updated_at": datetime.utcnow().isoformat(),
            "last_reviewed_by": analyst_name
        }
        if notes:
            update_doc["investigator_notes"] = notes

        if self.is_connected:
            result = self.db.alerts.update_one({"alert_id": alert_id}, {"$set": update_doc})
            return result.modified_count > 0
        else:
            for a in self._local_storage["alerts"]:
                if a.get("alert_id") == alert_id:
                    a.update(update_doc)
                    return True
            return False

    # ----------------------------------------------------
    # Report Operations
    # ----------------------------------------------------
    def save_report_record(self, report_record: Dict[str, Any]) -> str:
        """Store generated report metadata."""
        if not report_record.get("created_at"):
            report_record["created_at"] = datetime.utcnow().isoformat()
        if self.is_connected:
            self.db.reports.insert_one(report_record)
        else:
            self._local_storage["reports"].insert(0, report_record)
        return report_record.get("case_id", "CASE-UNKNOWN")

    def get_reports(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch list of all generated investigation reports."""
        if self.is_connected:
            return list(self.db.reports.find({}, {"_id": 0}).sort("created_at", -1).limit(limit))
        return self._local_storage["reports"][:limit]


# Global singleton instance
db_instance = DatabaseManager()

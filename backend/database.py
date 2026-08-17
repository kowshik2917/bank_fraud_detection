"""
Module 10: MongoDB Integration & Resilient Storage Layer
Intelligent Banking Fraud Detection Platform
"""

import os
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False


class DatabaseManager:
    """
    Unified MongoDB connection manager with resilient in-memory fallback.
    Collections: transactions, alerts, investigations, reports, users, search_logs
    """

    def __init__(self, uri: Optional[str] = None, db_name: Optional[str] = None):
        # Priority: explicit arg -> env var -> local MongoDB
        self.uri = uri or os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017")
        self.db_name = db_name or os.getenv("MONGODB_DB_NAME", "fraud_platform_db")
        self.client = None
        self.db = None
        self.is_connected = False

        self._local_storage = {
            "transactions": [],
            "alerts": [],
            "investigations": [],
            "reports": [],
            "users": [],
            "search_logs": []
        }
        self._init_connection()

    def _init_connection(self):
        """Attempt connection to MongoDB."""
        if PYMONGO_AVAILABLE:
            try:
                print(f"[MongoDB] Connecting to {self.uri} ...")
                self.client = MongoClient(self.uri, serverSelectionTimeoutMS=3000)
                self.client.admin.command('ping')
                self.db = self.client[self.db_name]
                self.is_connected = True
                print(f"[MongoDB] Connected to database '{self.db_name}'")
                self._setup_indexes()
                return
            except (ConnectionFailure, ServerSelectionTimeoutError, Exception) as e:
                print(f"[MongoDB] Connection failed ({e}). Using in-memory fallback.")
        else:
            print("[MongoDB] pymongo not installed. Using in-memory fallback.")
        self.is_connected = False

    def _setup_indexes(self):
        """Create performance indexes."""
        try:
            self.db.transactions.create_index("transaction_id", unique=True)
            self.db.transactions.create_index("timestamp")
            self.db.transactions.create_index("risk_level")
            self.db.alerts.create_index("alert_id", unique=True)
            self.db.alerts.create_index("status")
            self.db.alerts.create_index("created_at")
            self.db.reports.create_index("case_id", unique=True)
            self.db.users.create_index("email", unique=True)
            self.db.search_logs.create_index("timestamp")
        except Exception as e:
            print(f"[MongoDB] Index creation note: {e}")

    # --------------------------------------------------
    # Transaction Operations
    # --------------------------------------------------
    def insert_transaction(self, record: Dict[str, Any], user_email: Optional[str] = None) -> str:
        if not record.get("transaction_id"):
            record["transaction_id"] = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        if not record.get("timestamp"):
            record["timestamp"] = datetime.utcnow().isoformat()
        if user_email:
            record["user_email"] = user_email
        elif not record.get("user_email"):
            record["user_email"] = "default"

        if self.is_connected:
            self.db.transactions.update_one(
                {"transaction_id": record["transaction_id"]},
                {"$set": record},
                upsert=True
            )
        else:
            for i, r in enumerate(self._local_storage["transactions"]):
                if r.get("transaction_id") == record["transaction_id"]:
                    self._local_storage["transactions"][i] = record
                    return record["transaction_id"]
            self._local_storage["transactions"].insert(0, record)
        return record["transaction_id"]

    def get_transactions(
        self,
        limit: int = 50,
        skip: int = 0,
        risk_level: Optional[str] = None,
        search: Optional[str] = None,
        user_email: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if self.is_connected:
            query = {}
            if user_email:
                query["user_email"] = user_email
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
            if user_email:
                records = [r for r in records if r.get("user_email") == user_email]
            if risk_level and risk_level.upper() != "ALL":
                records = [r for r in records if r.get("risk_level", "").upper() == risk_level.upper()]
            if search:
                s = search.lower()
                records = [r for r in records if s in r.get("transaction_id", "").lower() or s in r.get("cardholder_id", "").lower()]
            return records[skip: skip + limit]

    # --------------------------------------------------
    # Alert Operations
    # --------------------------------------------------
    def insert_alert(self, alert_data: Dict[str, Any], user_email: Optional[str] = None) -> str:
        if not alert_data.get("alert_id"):
            alert_data["alert_id"] = f"ALT-{uuid.uuid4().hex[:6].upper()}"
        if not alert_data.get("created_at"):
            alert_data["created_at"] = datetime.utcnow().isoformat()
        if not alert_data.get("status"):
            alert_data["status"] = "OPEN"
        if user_email:
            alert_data["user_email"] = user_email
        elif not alert_data.get("user_email"):
            alert_data["user_email"] = "default"

        if self.is_connected:
            self.db.alerts.update_one(
                {"alert_id": alert_data["alert_id"]},
                {"$set": alert_data},
                upsert=True
            )
        else:
            for i, a in enumerate(self._local_storage["alerts"]):
                if a.get("alert_id") == alert_data["alert_id"]:
                    self._local_storage["alerts"][i] = alert_data
                    return alert_data["alert_id"]
            self._local_storage["alerts"].insert(0, alert_data)
        return alert_data["alert_id"]

    def get_alerts(
        self,
        status: Optional[str] = None,
        limit: Optional[int] = 50,
        user_email: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if self.is_connected:
            query = {}
            if user_email:
                query["user_email"] = user_email
            if status and status.upper() != "ALL":
                query["status"] = status.upper()
            cursor = self.db.alerts.find(query, {"_id": 0}).sort("created_at", -1)
            if limit is not None and limit > 0:
                cursor = cursor.limit(limit)
            return list(cursor)
        else:
            alerts = self._local_storage["alerts"]
            if user_email:
                alerts = [a for a in alerts if a.get("user_email") == user_email]
            if status and status.upper() != "ALL":
                alerts = [a for a in alerts if a.get("status", "").upper() == status.upper()]
            return alerts if (limit is None or limit == 0) else alerts[:limit]

    def update_alert_status(
        self,
        alert_id: str,
        new_status: str,
        notes: Optional[str] = None,
        analyst_name: str = "Lead Fraud Analyst"
    ) -> bool:
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

    # --------------------------------------------------
    # Report Operations
    # --------------------------------------------------
    def save_report_record(self, report_record: Dict[str, Any], user_email: Optional[str] = None) -> str:
        if not report_record.get("created_at"):
            report_record["created_at"] = datetime.utcnow().isoformat()
        case_id = report_record.get("case_id", f"CASE-{uuid.uuid4().hex[:6].upper()}")
        report_record["case_id"] = case_id
        if user_email:
            report_record["user_email"] = user_email
        elif not report_record.get("user_email"):
            report_record["user_email"] = "default"

        if self.is_connected:
            self.db.reports.update_one(
                {"case_id": case_id},
                {"$set": report_record},
                upsert=True
            )
        else:
            for i, r in enumerate(self._local_storage["reports"]):
                if r.get("case_id") == case_id:
                    self._local_storage["reports"][i] = report_record
                    return case_id
            self._local_storage["reports"].insert(0, report_record)
        return case_id

    def get_reports(self, limit: int = 50, user_email: Optional[str] = None) -> List[Dict[str, Any]]:
        if self.is_connected:
            query = {}
            if user_email:
                query["user_email"] = user_email
            return list(self.db.reports.find(query, {"_id": 0}).sort("created_at", -1).limit(limit))
        reports = self._local_storage["reports"]
        if user_email:
            reports = [r for r in reports if r.get("user_email") == user_email]
        return reports[:limit]

    # --------------------------------------------------
    # User / Auth Operations
    # --------------------------------------------------
    def upsert_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update a user. user dict: email, name, password_hash, role."""
        if not user.get("created_at"):
            user["created_at"] = datetime.utcnow().isoformat()
        user["last_login"] = datetime.utcnow().isoformat()
        if self.is_connected:
            self.db.users.update_one(
                {"email": user["email"]},
                {"$set": user},
                upsert=True
            )
            result = self.db.users.find_one({"email": user["email"]}, {"_id": 0, "password_hash": 0})
            return result or {}
        else:
            for u in self._local_storage["users"]:
                if u.get("email") == user["email"]:
                    u.update(user)
                    return {k: v for k, v in u.items() if k != "password_hash"}
            self._local_storage["users"].append(user)
            return {k: v for k, v in user.items() if k != "password_hash"}

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Fetch full user record (including password_hash) by email."""
        if self.is_connected:
            return self.db.users.find_one({"email": email}, {"_id": 0})
        for u in self._local_storage["users"]:
            if u.get("email") == email:
                return u
        return None

    # --------------------------------------------------
    # Search Log Operations
    # --------------------------------------------------
    def log_search(self, analyst_email: str, query: str, results_count: int = 0) -> str:
        """Record a search performed by an analyst."""
        log_id = f"SRCH-{uuid.uuid4().hex[:8].upper()}"
        log_record = {
            "log_id": log_id,
            "analyst_email": analyst_email,
            "query": query,
            "results_count": results_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        if self.is_connected:
            self.db.search_logs.insert_one(log_record)
        else:
            self._local_storage["search_logs"].insert(0, log_record)
        return log_id

    def get_search_logs(self, analyst_email: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent search logs, optionally filtered by analyst."""
        if self.is_connected:
            query = {}
            if analyst_email:
                query["analyst_email"] = analyst_email
            return list(self.db.search_logs.find(query, {"_id": 0}).sort("timestamp", -1).limit(limit))
        logs = self._local_storage["search_logs"]
        if analyst_email:
            logs = [l for l in logs if l.get("analyst_email") == analyst_email]
        return logs[:limit]


# Global singleton instance
db_instance = DatabaseManager()

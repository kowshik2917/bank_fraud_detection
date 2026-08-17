"""
Auth Route - User Login & Registration
Intelligent Banking Fraud Detection Platform
"""

import hashlib
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from backend.database import db_instance

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


def _hash_password(password: str) -> str:
    """Simple SHA-256 hash. Replace with bcrypt in production."""
    return hashlib.sha256(password.encode()).hexdigest()


class LoginRequest(BaseModel):
    email: str
    password: str
    name: str = ""


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    role: str = "analyst"


@router.post("/login")
def login(req: LoginRequest):
    """
    Authenticate a user.
    - If the user does not exist in MongoDB, auto-creates them (first-time login).
    - If the user exists, verifies the password hash.
    """
    existing = db_instance.get_user_by_email(req.email)
    pw_hash = _hash_password(req.password)

    if existing is None:
        # Auto-register on first login
        if not req.name:
            raise HTTPException(status_code=400, detail="Name is required for first-time login.")
        user_record = {
            "email": req.email,
            "name": req.name,
            "password_hash": pw_hash,
            "role": "analyst",
            "initials": "".join(part[0] for part in req.name.strip().split())[:2].upper()
        }
        profile = db_instance.upsert_user(user_record)
        return {"status": "registered", "profile": profile}
    else:
        if existing.get("password_hash") != pw_hash:
            raise HTTPException(status_code=401, detail="Invalid credentials.")
        # Update last_login timestamp
        profile = db_instance.upsert_user({
            "email": req.email,
            "name": existing.get("name", req.name),
            "password_hash": pw_hash,
            "role": existing.get("role", "analyst"),
            "initials": existing.get("initials", "")
        })
        return {"status": "authenticated", "profile": profile}


@router.post("/register")
def register(req: RegisterRequest):
    """Explicitly register a new analyst account."""
    existing = db_instance.get_user_by_email(req.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered.")
    pw_hash = _hash_password(req.password)
    user_record = {
        "email": req.email,
        "name": req.name,
        "password_hash": pw_hash,
        "role": req.role,
        "initials": "".join(part[0] for part in req.name.strip().split())[:2].upper()
    }
    profile = db_instance.upsert_user(user_record)
    return {"status": "registered", "profile": profile}


@router.get("/users")
def list_users():
    """List all registered analysts (admin use)."""
    if db_instance.is_connected:
        users = list(db_instance.db.users.find({}, {"_id": 0, "password_hash": 0}))
    else:
        users = [{k: v for k, v in u.items() if k != "password_hash"}
                 for u in db_instance._local_storage["users"]]
    return {"users": users, "total": len(users)}

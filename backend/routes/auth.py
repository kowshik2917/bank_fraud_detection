"""
Auth Route - User Login & Registration
Intelligent Banking Fraud Detection Platform
"""

import bcrypt
import re
import hashlib
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.database import db_instance

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


def _hash_password(password: str) -> str:
    """Hash a plain-text password with bcrypt (salted, adaptive cost)."""
    pwd_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')


def _verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(plain.encode('utf-8')[:72], hashed.encode('utf-8'))
    except Exception:
        return False


def _is_legacy_sha256(hashed: str) -> bool:
    """Detect old SHA-256 hex hashes (pre-bcrypt migration)."""
    return bool(re.fullmatch(r'[0-9a-f]{64}', hashed or ''))


def _sha256_hash(password: str) -> str:
    """Compute SHA-256 for migration comparison only."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


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

    - First-time login (user not in DB): auto-registers with a bcrypt password hash.
    - Existing user with bcrypt hash: verifies with bcrypt.
    - Existing user with legacy SHA-256 hash: transparently re-hashes to bcrypt on
      successful login (one-time migration, zero user friction).
    """
    existing = db_instance.get_user_by_email(req.email)

    if existing is None:
        # Auto-register on first login
        if not req.name:
            raise HTTPException(status_code=400, detail="Name is required for first-time login.")
        user_record = {
            "email": req.email,
            "name": req.name,
            "password_hash": _hash_password(req.password),
            "role": "analyst",
            "initials": "".join(part[0] for part in req.name.strip().split())[:2].upper()
        }
        profile = db_instance.upsert_user(user_record)
        return {"status": "registered", "profile": profile}

    stored_hash = existing.get("password_hash", "")

    # --- Legacy SHA-256 migration path ---
    if _is_legacy_sha256(stored_hash):
        if _sha256_hash(req.password) != stored_hash:
            raise HTTPException(status_code=401, detail="Invalid credentials.")
        # Password matched: silently upgrade to bcrypt
        new_hash = _hash_password(req.password)
        existing["password_hash"] = new_hash
        db_instance.upsert_user(existing)
        stored_hash = new_hash  # continue with updated hash

    # --- Normal bcrypt verification ---
    if not _verify_password(req.password, stored_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    profile = db_instance.upsert_user({
        "email": req.email,
        "name": existing.get("name", req.name),
        "password_hash": stored_hash,
        "role": existing.get("role", "analyst"),
        "initials": existing.get("initials", "")
    })
    return {"status": "authenticated", "profile": profile}


@router.post("/register")
def register(req: RegisterRequest):
    """Explicitly register a new analyst account with a bcrypt password hash."""
    existing = db_instance.get_user_by_email(req.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered.")
    user_record = {
        "email": req.email,
        "name": req.name,
        "password_hash": _hash_password(req.password),
        "role": req.role,
        "initials": "".join(part[0] for part in req.name.strip().split())[:2].upper()
    }
    profile = db_instance.upsert_user(user_record)
    return {"status": "registered", "profile": profile}


@router.get("/users")
def list_users():
    """List all registered analysts (admin use). Password hashes are never returned."""
    if db_instance.is_connected:
        users = list(db_instance.db.users.find({}, {"_id": 0, "password_hash": 0}))
    else:
        users = [{k: v for k, v in u.items() if k != "password_hash"}
                 for u in db_instance._local_storage["users"]]
    return {"users": users, "total": len(users)}

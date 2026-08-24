"""
DRISHTI - Authentication & RBAC (Role-Based Access Control)
-----------------------------------------------------------
- Passwords are hashed with PBKDF2-SHA256 (built into Python, no extra deps).
- Login returns a JWT token that the mobile app / dashboard sends with
  every request in the "Authorization: Bearer <token>" header.
- require_role("admin") guards endpoints so only the right role can call them.
"""

import hashlib
import os

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database import get_db
from models import User

# In production keep this in an environment variable — never commit real secrets!
SECRET_KEY = "drishti-demo-secret-change-me"
ALGORITHM = "HS256"
TOKEN_HOURS = 12

bearer_scheme = HTTPBearer(auto_error=False)


# ---------- password hashing (PBKDF2, stdlib only) ----------

def hash_password(password: str) -> str:
    """Store as: iterations$salt_hex$hash_hex"""
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return f"100000${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        iterations, salt_hex, hash_hex = stored.split("$")
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt_hex), int(iterations)
        )
        return digest.hex() == hash_hex
    except Exception:
        return False


# ---------- JWT tokens ----------

def create_access_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Decode the Bearer token and load the matching user from the DB."""
    if creds is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.get(User, int(payload["sub"]))
    if user is None:
        raise HTTPException(status_code=401, detail="User no longer exists")
    return user


def require_role(*roles: str):
    """Dependency factory: usage ->  user: User = Depends(require_role('admin'))"""

    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Requires role {'/'.join(roles)}, you are '{user.role}'",
            )
        return user

    return checker
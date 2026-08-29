"""
DRISHTI - Authentication & RBAC (Role-Based Access Control)
-----------------------------------------------------------
- Passwords are hashed with PBKDF2-SHA256 (built into Python, no extra deps).
- Login returns a JWT token that the mobile app / dashboard sends with
  every request in the "Authorization: Bearer <token>" header.
- Tokens carry an `exp` claim and are rejected when expired.
- require_role("admin") guards endpoints so only the right role can call them.
"""

import hashlib
import os
import secrets
import time
import threading
from collections import defaultdict, deque

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database import get_db
from models import User

# SECURITY: real secret comes from JWT_SECRET env var. A random fallback is
# generated at process start so a misconfigured production deploy doesn't
# silently fall back to a hard-coded value.
SECRET_KEY = os.environ.get("JWT_SECRET") or "INSECURE-" + secrets.token_urlsafe(32)
ALGORITHM = "HS256"
TOKEN_TTL_ADMIN_SECONDS     = int(os.environ.get("JWT_ADMIN_EXPIRE_SECONDS",     "28800"))  #  8h
TOKEN_TTL_INSPECTOR_SECONDS = int(os.environ.get("JWT_INSPECTOR_EXPIRE_SECONDS", "86400"))  # 24h
TOKEN_TTL_NGO_SECONDS       = int(os.environ.get("JWT_NGO_EXPIRE_SECONDS",      "43200"))  # 12h
REFRESH_GRACE_SECONDS       = int(os.environ.get("JWT_REFRESH_GRACE_SECONDS",   "3600"))   #  1h

bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
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


def _ttl_for(role: str) -> int:
    return {
        "admin":     TOKEN_TTL_ADMIN_SECONDS,
        "inspector": TOKEN_TTL_INSPECTOR_SECONDS,
        "institute": TOKEN_TTL_NGO_SECONDS,
    }.get(role, TOKEN_TTL_INSPECTOR_SECONDS)


def create_access_token(user: User) -> str:
    """Issue a JWT with an explicit `exp` (expiry) claim."""
    now = int(time.time())
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
        "iat": now,
        "exp": now + _ttl_for(user.role),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str, *, allow_grace: bool = False) -> dict:
    """
    Decode a JWT and return its payload, or raise 401.
    With `allow_grace=True` (used by /auth/refresh) tokens expired for
    no more than REFRESH_GRACE_SECONDS are still accepted.
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        if allow_grace:
            try:
                return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM],
                                  options={"verify_exp": False})
            except jwt.PyJWTError as e:
                raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if creds is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(creds.credentials)
    user = db.get(User, int(payload["sub"]))
    if user is None:
        raise HTTPException(status_code=401, detail="User no longer exists")
    return user


def require_role(*roles: str):
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Requires role {'/'.join(roles)}, you are '{user.role}'",
            )
        return user
    return checker


# ---------- simple login rate-limit (per username, in-memory) ----------
# Locks the username for LOCKOUT_SECONDS after MAX_ATTEMPTS within WINDOW_SECONDS.
# In-memory is fine for one-process; for a multi-worker prod deploy swap
# this for a Redis counter.
_LOGIN_WINDOW = 60       # seconds
_LOGIN_MAX    = 5        # attempts per window
_LOGIN_LOCK   = 60       # extra lockout after the limit is hit
_attempts = defaultdict(lambda: deque(maxlen=_LOGIN_MAX))
_locks    = {}
_lock_mu  = threading.Lock()


def login_rate_limit_check(username: str) -> None:
    with _lock_mu:
        now = time.time()
        if username in _locks and _locks[username] > now:
            raise HTTPException(
                status_code=429,
                detail=f"Too many login attempts. Try again in "
                       f"{int(_locks[username] - now)}s.",
            )
        window = _attempts[username]
        while window and window[0] < now - _LOGIN_WINDOW:
            window.popleft()
        if len(window) >= _LOGIN_MAX:
            _locks[username] = now + _LOGIN_LOCK
            window.clear()
            raise HTTPException(
                status_code=429,
                detail=f"Too many login attempts. Locked for {_LOGIN_LOCK}s.",
            )


def login_rate_limit_record(username: str) -> None:
    with _lock_mu:
        _attempts[username].append(time.time())
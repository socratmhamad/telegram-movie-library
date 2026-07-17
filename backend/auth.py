"""Authentication utilities — password hashing, JWT tokens, rate limiting."""

from __future__ import annotations

import os
import secrets
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
import bcrypt
from pydantic import BaseModel, field_validator

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_JWT_SECRET = os.getenv("ADMIN_JWT_SECRET", "")
_JWT_ALGORITHM = "HS256"
_ACCESS_TOKEN_EXPIRE_MINUTES = 15
_REFRESH_TOKEN_EXPIRE_DAYS = 7

_ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

if not _JWT_SECRET:
    raise RuntimeError(
        "Missing required environment variable: ADMIN_JWT_SECRET. "
        "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
    )

if not _ADMIN_PASSWORD:
    raise RuntimeError("Missing required environment variable: ADMIN_PASSWORD")

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

_HASHED_PASSWORD = bcrypt.hashpw(_ADMIN_PASSWORD.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str) -> bool:
    """Verify a plaintext password against the stored bcrypt hash.

    bcrypt.checkpw is inherently constant-time for the hash comparison.
    """
    return bcrypt.checkpw(plain.encode("utf-8"), _HASHED_PASSWORD.encode("utf-8"))


def verify_username(candidate: str) -> bool:
    """Constant-time username comparison to prevent timing oracles."""
    return secrets.compare_digest(candidate, _ADMIN_USERNAME)


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=_ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": subject, "exp": expire, "type": "access"},
        _JWT_SECRET,
        algorithm=_JWT_ALGORITHM,
    )


def create_refresh_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=_REFRESH_TOKEN_EXPIRE_DAYS)
    jti = secrets.token_hex(16)
    return jwt.encode(
        {"sub": subject, "exp": expire, "type": "refresh", "jti": jti},
        _JWT_SECRET,
        algorithm=_JWT_ALGORITHM,
    )


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token. Raises HTTPException on failure."""
    try:
        payload = jwt.decode(token, _JWT_SECRET, algorithms=[_JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ---------------------------------------------------------------------------
# Refresh token blocklist (in-memory, resets on server restart)
#
# LIMITATION: This blocklist is lost on process restart and is not shared
# across multiple workers/instances.  For single-process deployments (e.g.
# Render free tier with a single Uvicorn worker) this is acceptable.
# For multi-process or multi-instance deployments, replace with a
# Redis-backed set or a database table.
# ---------------------------------------------------------------------------

_blocked_jtis: set[str] = set()


def block_refresh_token(token: str) -> None:
    """Add a refresh token's JTI to the blocklist."""
    try:
        payload = jwt.decode(token, _JWT_SECRET, algorithms=[_JWT_ALGORITHM])
        jti = payload.get("jti")
        if jti:
            _blocked_jtis.add(jti)
    except JWTError:
        pass  # already invalid, nothing to block


def is_refresh_blocked(payload: dict) -> bool:
    jti = payload.get("jti")
    return jti in _blocked_jtis if jti else False


# ---------------------------------------------------------------------------
# Rate limiting (sliding window per IP)
# ---------------------------------------------------------------------------

_MAX_LOGIN_ATTEMPTS = 5
_WINDOW_SECONDS = 300  # 5 minutes
_login_attempts: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(client_ip: str) -> None:
    """Raise 429 if client has exceeded login attempt limit."""
    now = time.time()
    cutoff = now - _WINDOW_SECONDS
    # Prune old entries
    _login_attempts[client_ip] = [t for t in _login_attempts[client_ip] if t > cutoff]
    if len(_login_attempts[client_ip]) >= _MAX_LOGIN_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again later.",
        )


def record_login_attempt(client_ip: str) -> None:
    """Record a failed login attempt for rate limiting."""
    _login_attempts[client_ip].append(time.time())


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    username: str
    password: str

    @field_validator("username", "password")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = _ACCESS_TOKEN_EXPIRE_MINUTES * 60


class RefreshRequest(BaseModel):
    refresh_token: str


class AdminInfoResponse(BaseModel):
    username: str
    role: str = "admin"


# ---------------------------------------------------------------------------
# FastAPI dependency — protect admin routes
# ---------------------------------------------------------------------------

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_admin(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> str:
    """Dependency that validates the JWT access token and returns the admin username."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(credentials.credentials)

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username: str | None = payload.get("sub")
    if not username or not verify_username(username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    return username

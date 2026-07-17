"""Authentication API router — login, token refresh, logout."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status

from backend.auth import (
    AdminInfoResponse,
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    block_refresh_token,
    check_rate_limit,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_admin,
    is_refresh_blocked,
    record_login_attempt,
    verify_password,
    verify_username,
    _ADMIN_USERNAME,
)

router = APIRouter(prefix="/api/admin", tags=["auth"])


def _client_ip(request: Request) -> str:
    """Extract client IP, respecting X-Forwarded-For behind a reverse proxy.

    Uses the **rightmost** entry in X-Forwarded-For, which is the IP
    appended by the last trusted reverse proxy (e.g. Render, Cloudflare).
    The leftmost entry is trivially spoofable by the client.
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        # Rightmost IP is set by the nearest trusted proxy
        parts = [p.strip() for p in forwarded.split(",") if p.strip()]
        return parts[-1] if parts else (request.client.host if request.client else "unknown")
    return request.client.host if request.client else "unknown"


@router.post("/login", response_model=TokenResponse)
def admin_login(body: LoginRequest, request: Request):
    """Authenticate admin and return access + refresh tokens."""
    ip = _client_ip(request)
    check_rate_limit(ip)

    # Always run both checks to prevent timing oracles.
    # verify_username uses secrets.compare_digest (constant-time).
    # verify_password uses bcrypt.checkpw (constant-time by design).
    username_ok = verify_username(body.username)
    password_ok = verify_password(body.password)

    if not (username_ok and password_ok):
        record_login_attempt(ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    return TokenResponse(
        access_token=create_access_token(body.username),
        refresh_token=create_refresh_token(body.username),
    )


@router.post("/refresh", response_model=TokenResponse)
def admin_refresh(body: RefreshRequest):
    """Exchange a valid refresh token for a new access + refresh token pair."""
    payload = decode_token(body.refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    if is_refresh_blocked(payload):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )

    username = payload.get("sub")
    if not username or not verify_username(username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    # Block the old refresh token (rotation)
    block_refresh_token(body.refresh_token)

    return TokenResponse(
        access_token=create_access_token(username),
        refresh_token=create_refresh_token(username),
    )


@router.post("/logout", status_code=204)
def admin_logout(body: RefreshRequest):
    """Invalidate the refresh token."""
    block_refresh_token(body.refresh_token)
    return None


@router.get("/me", response_model=AdminInfoResponse)
def admin_me(username: str = Depends(get_current_admin)):
    """Return current admin info (validates token is active)."""
    return AdminInfoResponse(username=username)

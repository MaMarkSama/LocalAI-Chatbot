# -*- coding: utf-8 -*-
import os
import secrets
import time
from collections import defaultdict, deque
from typing import Callable, Optional

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))
AUTH_RATE_LIMIT_PER_MINUTE = int(os.getenv("AUTH_RATE_LIMIT_PER_MINUTE", "20"))
MAX_REQUEST_BYTES = int(os.getenv("MAX_REQUEST_BYTES", str(25 * 1024 * 1024)))
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "0").lower() in ("1", "true", "yes")
TRUST_PROXY_HEADERS = os.getenv("TRUST_PROXY_HEADERS", "0").lower() in ("1", "true", "yes")
TRUSTED_PROXIES = set(
    p.strip() for p in os.getenv("TRUSTED_PROXIES", "127.0.0.1,::1").split(",") if p.strip()
)
CSP_STRICT = os.getenv("CSP_STRICT", "0").lower() in ("1", "true", "yes")
CSP_ENABLE_NONCE = os.getenv("CSP_ENABLE_NONCE", "0").lower() in ("1", "true", "yes")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        length = request.headers.get("content-length")
        if length:
            try:
                if int(length) > MAX_REQUEST_BYTES:
                    return JSONResponse({"ok": False, "error": "request too large"}, status_code=413)
            except ValueError:
                return JSONResponse({"ok": False, "error": "invalid content-length"}, status_code=400)

        # Generate per-request cryptographic nonce for script and style authorization
        nonce = secrets.token_urlsafe(16)
        request.state.csp_nonce = nonce

        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.headers.setdefault("Cache-Control", "no-store")

        # Browser Content-Security-Policy:
        # If CSP_ENABLE_NONCE is True, emit per-request nonces.
        # Otherwise, use standard 'unsafe-inline' so inline event handlers (onclick) are not blocked by browsers.
        if CSP_ENABLE_NONCE:
            inline_fallback = " 'unsafe-inline'" if not CSP_STRICT else ""
            script_src = f"script-src 'self' 'nonce-{nonce}'{inline_fallback} https://cdnjs.cloudflare.com;"
        else:
            script_src = "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com;"

        csp_header = (
            f"default-src 'self'; "
            f"{script_src} "
            f"style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            f"font-src 'self' https://fonts.gstatic.com data:; "
            f"img-src 'self' data: blob: https:; "
            f"connect-src 'self'; "
            f"frame-ancestors 'none'; "
            f"base-uri 'self'; "
            f"form-action 'self'"
        )
        response.headers.setdefault("Content-Security-Policy", csp_header)

        is_https = (
            COOKIE_SECURE
            or request.url.scheme == "https"
            or request.headers.get("x-forwarded-proto") == "https"
        )
        if is_https:
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response


class InMemoryRateLimiter:
    def __init__(self, max_keys: int = 4096):
        self._hits = defaultdict(deque)
        self._max_keys = max_keys

    def allow(self, key: str, limit: int, window_seconds: int = 60) -> bool:
        now = time.time()
        if len(self._hits) > self._max_keys:
            expired = [k for k, q in self._hits.items() if not q or q[-1] <= now - window_seconds]
            for k in expired:
                self._hits.pop(k, None)
        hits = self._hits[key]
        while hits and hits[0] <= now - window_seconds:
            hits.popleft()
        if len(hits) >= limit:
            return False
        hits.append(now)
        return True


rate_limiter = InMemoryRateLimiter()


async def rate_limit(request: Request):
    client_host = request.client.host if request.client else "unknown"
    forwarded = request.headers.get("x-forwarded-for", "")

    # Only trust X-Forwarded-For if explicitly enabled and direct connection comes from an authorized reverse proxy IP
    if TRUST_PROXY_HEADERS and forwarded and client_host in TRUSTED_PROXIES:
        ip = forwarded.split(",")[0].strip()
    else:
        ip = client_host

    limit = AUTH_RATE_LIMIT_PER_MINUTE if request.url.path.startswith("/api/auth") else RATE_LIMIT_PER_MINUTE
    if not rate_limiter.allow(f"{ip}:{request.url.path}", limit):
        return JSONResponse({"ok": False, "error": "rate limit exceeded"}, status_code=429)
    return None


def cookie_options(request: Optional[Request] = None) -> dict:
    is_secure = COOKIE_SECURE
    if not is_secure and request:
        if request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https":
            is_secure = True

    return {
        "max_age": 86400 * int(os.getenv("TOKEN_EXPIRE_DAYS", "30")),
        "httponly": True,
        "samesite": os.getenv("COOKIE_SAMESITE", "lax"),
        "secure": is_secure,
    }

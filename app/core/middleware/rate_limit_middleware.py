import json
import threading
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings

AUTH_PATHS = (
    "/api/v1/auth/token",
    "/api/v1/auth/register",
    "/api/v1/auth/login",
)

EXCLUDED_PATHS = {
    "/health",
    "/",
    "/favicon.ico",
    "/openapi.json",
    "/docs",
    "/redoc",
}


class TokenBucket:
    """Token Bucket rate limiter — thread-safe.

    Tokens refill continuously at `refill_rate` tokens/second up to `capacity`.
    """

    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate)
        self.tokens = float(capacity)
        self.last_refill = time.monotonic()
        self._lock = threading.Lock()

    def try_consume(self, tokens: float = 1.0) -> bool:
        """Try to consume `tokens`. Returns True if allowed, False if rate limited."""
        with self._lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

    def reset(self) -> None:
        """Reset bucket to full capacity (for tests)."""
        with self._lock:
            self.tokens = float(self.capacity)
            self.last_refill = time.monotonic()

    @property
    def remaining(self) -> int:
        with self._lock:
            self._refill()
            return int(self.tokens)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """HTTP middleware that applies Token Bucket rate limiting per client IP.

    Two limiter configurations:
      - auth: strict, for AUTH_PATHS (login/register/token)
      - default: for all other paths (except EXCLUDED_PATHS)

    Each client IP gets its own TokenBucket, created on first request.
    """

    _instances: list["RateLimitMiddleware"] = []

    def __init__(self, app):
        super().__init__(app)
        self.auth_burst = settings.RATE_LIMIT_AUTH_BURST
        self.auth_per_minute = settings.RATE_LIMIT_AUTH_PER_MINUTE
        self.default_burst = settings.RATE_LIMIT_DEFAULT_BURST
        self.default_per_minute = settings.RATE_LIMIT_DEFAULT_PER_MINUTE

        self._auth_buckets: dict[str, TokenBucket] = {}
        self._default_buckets: dict[str, TokenBucket] = {}
        self._buckets_lock = threading.Lock()

        RateLimitMiddleware._instances.append(self)

    @classmethod
    def reset_all_limiters(cls) -> None:
        """Reset all per-IP buckets to full capacity (for tests)."""
        for instance in cls._instances:
            with instance._buckets_lock:
                instance._auth_buckets.clear()
                instance._default_buckets.clear()

    def _get_or_create_bucket(self, ip: str, is_auth: bool) -> TokenBucket:
        buckets = self._auth_buckets if is_auth else self._default_buckets
        with self._buckets_lock:
            if ip not in buckets:
                if is_auth:
                    buckets[ip] = TokenBucket(
                        capacity=self.auth_burst,
                        refill_rate=self.auth_per_minute / 60.0,
                    )
                else:
                    buckets[ip] = TokenBucket(
                        capacity=self.default_burst,
                        refill_rate=self.default_per_minute / 60.0,
                    )
            return buckets[ip]

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Skip excluded paths
        if path in EXCLUDED_PATHS:
            return await call_next(request)

        # Determine client IP
        client_ip = self._get_client_ip(request)

        # Select limiter config
        if path in AUTH_PATHS:
            is_auth = True
            limit = self.auth_per_minute
        else:
            is_auth = False
            limit = self.default_per_minute

        bucket = self._get_or_create_bucket(client_ip, is_auth)

        if not bucket.try_consume():
            retry_after = max(1, int(60.0 / bucket.refill_rate))
            headers = {
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": "0",
            }
            return Response(
                content=json.dumps({"detail": "Demasiadas solicitudes. Intente de nuevo más tarde."}),
                status_code=429,
                media_type="application/json",
                headers=headers,
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(bucket.remaining)
        return response

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """Extract client IP, supporting X-Forwarded-For header."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"

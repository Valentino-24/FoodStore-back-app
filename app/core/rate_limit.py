import time
from collections import defaultdict
from threading import Lock


class RateLimiter:
    """Sliding-window in-memory rate limiter."""

    def __init__(self, max_attempts: int = 5, window_minutes: int = 15):
        self.max_attempts = max_attempts
        self.window = window_minutes * 60  # seconds
        self._attempts: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        cutoff = now - self.window
        with self._lock:
            self._attempts[key] = [t for t in self._attempts[key] if t > cutoff]
            return len(self._attempts[key]) < self.max_attempts

    def record_failure(self, key: str) -> None:
        now = time.time()
        with self._lock:
            self._attempts[key].append(now)

    def reset(self, key: str) -> None:
        with self._lock:
            self._attempts.pop(key, None)


login_limiter = RateLimiter()

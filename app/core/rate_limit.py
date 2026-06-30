import time
from collections import defaultdict
from threading import Lock


class RateLimiter:
    """Rate limiter en memoria para endpoints de autenticación.

    Máximo 5 intentos fallidos por IP en 15 minutos.
    Responde HTTP 429 con header Retry-After indicando los segundos restantes.
    """

    def __init__(self, max_attempts: int = 5, window_minutes: int = 15):
        self.max_attempts = max_attempts
        self.window = window_minutes * 60
        self._attempts: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def is_allowed(self, key: str) -> bool:
        """Retorna True si la key no excedió el límite."""
        self._cleanup(key)
        with self._lock:
            return len(self._attempts[key]) < self.max_attempts

    def until_reset(self, key: str) -> int:
        """Segundos restantes hasta que la key pueda reintentar.
        Retorna 0 si ya está permitida."""
        self._cleanup(key)
        with self._lock:
            entries = self._attempts[key]
            if not entries or len(entries) < self.max_attempts:
                return 0
            oldest = min(entries)
            remaining = self.window - (time.time() - oldest)
            return max(1, int(remaining))

    def record_failure(self, key: str) -> None:
        now = time.time()
        with self._lock:
            self._attempts[key].append(now)

    def reset(self, key: str) -> None:
        """Limpia el contador de una key (ej: login exitoso)."""
        with self._lock:
            self._attempts.pop(key, None)

    def _cleanup(self, key: str) -> None:
        """Elimina timestamps fuera de la ventana."""
        now = time.time()
        cutoff = now - self.window
        with self._lock:
            self._attempts[key] = [t for t in self._attempts[key] if t > cutoff]


login_limiter = RateLimiter()

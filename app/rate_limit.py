from collections import deque
from threading import Lock
from time import monotonic


class RateLimiter:
    def __init__(self):
        self._hits: dict[str, deque[float]] = {}
        self._lock = Lock()

    def clear(self) -> None:
        with self._lock:
            self._hits.clear()

    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> tuple[bool, int]:
        now = monotonic()
        window_start = now - window_seconds

        with self._lock:
            bucket = self._hits.setdefault(key, deque())

            while bucket and bucket[0] <= window_start:
                bucket.popleft()

            if len(bucket) >= max_requests:
                retry_after = max(1, int(window_seconds - (now - bucket[0])))
                return False, retry_after

            bucket.append(now)
            return True, 0

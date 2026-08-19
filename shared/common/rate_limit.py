from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from time import monotonic


class SessionRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._buckets: dict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    def _pruned_bucket(self, key: str, now: float) -> deque[float]:
        bucket = self._buckets[key]
        while bucket and bucket[0] <= now - self.window_seconds:
            bucket.popleft()
        return bucket

    async def allow(self, key: str) -> bool:
        return await self.allow_all([key])

    async def allow_all(self, keys: list[str]) -> bool:
        """Allow the request only if every key still has room in its window.

        Used to rate-limit on both the session cookie and the client IP, so a
        client can't reset its quota by simply dropping/rotating the cookie.
        """
        async with self._lock:
            now = monotonic()
            buckets = [self._pruned_bucket(key, now) for key in keys]
            if any(len(bucket) >= self.max_requests for bucket in buckets):
                return False
            for bucket in buckets:
                bucket.append(now)
            return True

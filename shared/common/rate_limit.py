from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from time import monotonic


class SessionRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._buckets: dict[str, deque[float]] = defaultdict(deque)
        self._locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    async def allow(self, session_id: str) -> bool:
        async with self._locks[session_id]:
            now = monotonic()
            bucket = self._buckets[session_id]
            while bucket and bucket[0] <= now - self.window_seconds:
                bucket.popleft()
            if len(bucket) >= self.max_requests:
                return False
            bucket.append(now)
            return True

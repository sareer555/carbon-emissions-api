"""Short-window burst rate limiting, per API key.

Defaults to a zero-dependency in-memory fixed-window counter, which is fine
for a single-instance free-tier deployment (Render/Fly.io). Set REDIS_URL
(e.g. an Upstash Redis free tier) to make the limiter correct across
multiple instances/workers.
"""
import time
from collections import defaultdict
from threading import Lock

from fastapi import Depends

from app.auth import Caller, authenticate
from app.config import get_settings
from app.errors import RateLimitedError

settings = get_settings()


class InMemoryWindowLimiter:
    def __init__(self, limit_per_minute: int):
        self.limit = limit_per_minute
        self._counts: dict[str, tuple[int, int]] = defaultdict(lambda: (0, 0))  # key -> (window_start, count)
        self._lock = Lock()

    def check(self, identifier: str) -> None:
        window = int(time.time() // 60)
        with self._lock:
            window_start, count = self._counts[identifier]
            if window_start != window:
                window_start, count = window, 0
            count += 1
            self._counts[identifier] = (window_start, count)
        if count > self.limit:
            raise RateLimitedError(
                f"Rate limit of {self.limit} requests/minute exceeded. Please slow down."
            )


class RedisWindowLimiter:
    def __init__(self, redis_url: str, limit_per_minute: int):
        import redis  # imported lazily so redis-py is only required when configured

        self.client = redis.from_url(redis_url)
        self.limit = limit_per_minute

    def check(self, identifier: str) -> None:
        window = int(time.time() // 60)
        redis_key = f"ratelimit:{identifier}:{window}"
        count = self.client.incr(redis_key)
        if count == 1:
            self.client.expire(redis_key, 60)
        if count > self.limit:
            raise RateLimitedError(
                f"Rate limit of {self.limit} requests/minute exceeded. Please slow down."
            )


def _build_limiter():
    if settings.redis_url:
        return RedisWindowLimiter(settings.redis_url, settings.burst_limit_per_minute)
    return InMemoryWindowLimiter(settings.burst_limit_per_minute)


_limiter = _build_limiter()


def enforce_rate_limit(caller: Caller = Depends(authenticate)) -> Caller:
    """FastAPI dependency: run auth first (authenticate), then burst rate limiting.

    Returns the authenticated Caller so route handlers can depend on this
    single function to get both auth and rate limiting.
    """
    _limiter.check(caller.rate_limit_key)
    return caller

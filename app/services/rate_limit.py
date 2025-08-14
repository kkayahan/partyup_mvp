import time
import redis
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.core.config import settings

r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit:int=60, window:int=60):
        super().__init__(app)
        self.limit = limit
        self.window = window

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "unknown"
        key = f"rl:{ip}:{request.url.path}"
        with r.pipeline() as pipe:
            try:
                pipe.watch(key)
                current = r.get(key)
                if current is None:
                    pipe.multi()
                    pipe.set(key, 1, ex=self.window)
                    pipe.execute()
                    current = 1
                else:
                    current = int(current)
                    if current >= self.limit:
                        ttl = r.ttl(key)
                        return JSONResponse({"detail": "Rate limit exceeded", "retry_after": ttl}, status_code=429)
                    pipe.multi()
                    pipe.incr(key)
                    pipe.execute()
            except redis.WatchError:
                pass
        response = await call_next(request)
        return response

import time
import logging
import json
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from threading import Lock
from collections import defaultdict
from typing import Dict, List

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_logger")


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Logs requests in a structured, queryable, and standardized JSON format."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        method = request.method

        response = await call_next(request)

        duration = time.time() - start_time
        status_code = response.status_code

        # Structured log details
        log_payload = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "method": method,
            "path": path,
            "status_code": status_code,
            "client_ip": client_ip,
            "duration_ms": round(duration * 1000, 2),
        }

        # Log at appropriate levels
        if status_code >= 500:
            logger.error(json.dumps(log_payload))
        elif status_code >= 400:
            logger.warning(json.dumps(log_payload))
        else:
            logger.info(json.dumps(log_payload))

        return response


class RateLimiter:
    """Thread-safe sliding window rate limiter."""

    def __init__(self, requests_limit: int = 100, window_seconds: int = 60):
        self.limit = requests_limit
        self.window = window_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.lock = Lock()

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        with self.lock:
            # Clean expired timestamps
            self.requests[client_ip] = [
                t for t in self.requests[client_ip] if now - t < self.window
            ]

            if len(self.requests[client_ip]) >= self.limit:
                return False

            self.requests[client_ip].append(now)
            return True


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Enforces API rate limits per IP address."""

    def __init__(self, app, requests_limit: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.limiter = RateLimiter(requests_limit, window_seconds)

    async def dispatch(self, request: Request, call_next) -> Response:
        # Exclude documentation / swagger from rate limits
        if request.url.path in ("/docs", "/redoc", "/openapi.json", "/swagger", "/health"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"

        if not self.limiter.is_allowed(client_ip):
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please try again after some time.",
                    "ip": client_ip,
                },
            )

        return await call_next(request)

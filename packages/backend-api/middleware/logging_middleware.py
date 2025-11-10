"""
Logging middleware for automatic request/response tracking.

Logs all incoming requests and outgoing responses with timing information.
"""

import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs all HTTP requests and responses.

    For each request, logs:
    - Request ID (generated UUID)
    - HTTP method and path
    - Client IP address
    - Request duration in milliseconds
    - Response status code
    - User agent

    This middleware is completely free and uses only built-in Python logging.
    """

    def __init__(self, app: ASGIApp, exclude_paths: list[str] = None):
        """
        Initialize logging middleware.

        Args:
            app: FastAPI application
            exclude_paths: List of paths to exclude from logging (e.g., ["/health", "/"])
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or []

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details."""
        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Skip logging for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # Start timer
        start_time = time.time()

        # Extract request details
        method = request.method
        path = request.url.path
        query_params = str(request.query_params) if request.query_params else None
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Log incoming request
        logger.info(
            f"Incoming request: {method} {path}",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "query_params": query_params,
                "client_ip": client_ip,
                "user_agent": user_agent,
            }
        )

        # Add request_id to request state for use in route handlers
        request.state.request_id = request_id

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log response
            logger.info(
                f"Request completed: {method} {path} - {response.status_code}",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 2),
                }
            )

            # Add request ID to response headers for tracing
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log error
            logger.error(
                f"Request failed: {method} {path} - {str(e)}",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "duration_ms": round(duration_ms, 2),
                    "error": str(e),
                },
                exc_info=True
            )

            raise

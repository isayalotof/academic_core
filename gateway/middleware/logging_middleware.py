"""
Logging Middleware
Middleware для логирования HTTP запросов
"""

import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования запросов и ответов"""

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Обработать запрос и залогировать информацию

        Args:
            request: HTTP запрос
            call_next: Следующий middleware/handler

        Returns:
            HTTP ответ
        """
        start_time = time.time()

        # Log request
        logger.info(
            "Request started",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_host": (
                    request.client.host if request.client else None
                )
            }
        )

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log response
        logger.info(
            "Request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_seconds": round(duration, 3)
            }
        )

        # Update metrics (skip /metrics endpoint itself)
        if request.url.path != "/metrics":
            try:
                import main
                main.request_count += 1
                main.request_duration_sum += duration
            except Exception:
                pass

        # Add custom headers
        response.headers["X-Response-Time"] = f"{duration:.3f}s"

        return response

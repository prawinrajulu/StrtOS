import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import logger

class RequestCorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        correlation_id = request.headers.get("X-Correlation-ID", request_id)
        
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id
        
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Process-Time-MS"] = f"{process_time:.2f}"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        logger.info(
            f"HTTP {request.method} {request.url.path} - Status: {response.status_code} - Duration: {process_time:.2f}ms - RequestID: {request_id}"
        )

        return response

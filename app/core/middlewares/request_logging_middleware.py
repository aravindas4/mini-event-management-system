import logging
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.middlewares.trace_context_middleware import get_trace_id, get_request_id

logger = logging.getLogger("event_management.requests")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Enhanced request logging with trace context"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get trace context
        trace_id = get_trace_id()
        request_id = get_request_id()
        
        # Log request start
        start_time = time.time()
        logger.info(
            "Request started",
            extra={
                "trace_id": trace_id,
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "endpoint": request.url.path,
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown")
            }
        )
        
        # Process request
        response = await call_next(request)
        
        # Log request completion
        process_time = time.time() - start_time
        logger.info(
            "Request completed",
            extra={
                "trace_id": trace_id,
                "request_id": request_id,
                "method": request.method,
                "endpoint": request.url.path,
                "status_code": response.status_code,
                "process_time": f"{process_time:.4f}s"
            }
        )
        
        return response
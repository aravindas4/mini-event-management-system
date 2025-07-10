import logging
import uuid
from contextvars import ContextVar
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# ContextVar for trace ID - automatically inherited by async tasks
trace_id_var: ContextVar[Optional[str]] = ContextVar('trace_id', default=None)
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
event_id_var: ContextVar[Optional[str]] = ContextVar('event_id', default=None)

logger = logging.getLogger("event_management.trace")

class TraceContextMiddleware(BaseHTTPMiddleware):
    """Middleware to manage trace context using ContextVars"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate trace ID and request ID
        trace_id = request.headers.get("X-Trace-ID") or str(uuid.uuid4())
        request_id = str(uuid.uuid4())
        
        # Set context variables
        trace_id_var.set(trace_id)
        request_id_var.set(request_id)
        
        # Store in request state for backward compatibility
        request.state.trace_id = trace_id
        request.state.request_id = request_id
        
        logger.debug(
            "Trace context initialized",
            extra={
                "trace_id": trace_id,
                "request_id": request_id,
                "method": request.method,
                "endpoint": request.url.path
            }
        )
        
        try:
            # Process request with context
            response = await call_next(request)
            
            # Add trace headers to response
            response.headers["X-Trace-ID"] = trace_id
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        finally:
            # Clean up context variables
            trace_id_var.set(None)
            request_id_var.set(None)
            event_id_var.set(None)

def get_trace_id() -> Optional[str]:
    """Get current trace ID from context"""
    return trace_id_var.get()

def get_request_id() -> Optional[str]:
    """Get current request ID from context"""
    return request_id_var.get()

def get_event_id() -> Optional[str]:
    """Get current event ID from context"""
    return event_id_var.get()

def set_event_id(event_id: str) -> None:
    """Set event ID in context"""
    event_id_var.set(event_id)
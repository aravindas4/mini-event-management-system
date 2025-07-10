import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.middlewares.trace_context_middleware import get_trace_id, get_request_id, get_event_id
from app.core.exceptions import EventNotFound, CapacityExceeded, DuplicateRegistration, ValidationError

logger = logging.getLogger("event_management.errors")

async def event_not_found_handler(request: Request, exc: EventNotFound):
    """Handle event not found errors with trace context"""
    trace_id = get_trace_id()
    request_id = get_request_id()
    event_id = get_event_id()
    
    logger.warning(
        "Event not found",
        extra={
            "trace_id": trace_id,
            "request_id": request_id,
            "event_id": event_id,
            "error_type": "EventNotFound",
            "error_message": str(exc),
            "endpoint": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=404,
        content={
            "error": "Event not found",
            "message": str(exc),
            "trace_id": trace_id,
            "request_id": request_id
        }
    )

async def capacity_exceeded_handler(request: Request, exc: CapacityExceeded):
    """Handle capacity exceeded errors with trace context"""
    trace_id = get_trace_id()
    request_id = get_request_id()
    event_id = get_event_id()
    
    logger.warning(
        "Event capacity exceeded",
        extra={
            "trace_id": trace_id,
            "request_id": request_id,
            "event_id": event_id,
            "error_type": "CapacityExceeded",
            "error_message": str(exc),
            "endpoint": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=409,
        content={
            "error": "Capacity exceeded",
            "message": str(exc),
            "trace_id": trace_id,
            "request_id": request_id
        }
    )

async def duplicate_registration_handler(request: Request, exc: DuplicateRegistration):
    """Handle duplicate registration errors with trace context"""
    trace_id = get_trace_id()
    request_id = get_request_id()
    event_id = get_event_id()
    
    logger.warning(
        "Duplicate registration attempt",
        extra={
            "trace_id": trace_id,
            "request_id": request_id,
            "event_id": event_id,
            "error_type": "DuplicateRegistration",
            "error_message": str(exc),
            "endpoint": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=409,
        content={
            "error": "Duplicate registration",
            "message": str(exc),
            "trace_id": trace_id,
            "request_id": request_id
        }
    )

async def validation_error_handler(request: Request, exc: ValidationError):
    """Handle validation errors with trace context"""
    trace_id = get_trace_id()
    request_id = get_request_id()
    event_id = get_event_id()
    
    logger.warning(
        "Validation error",
        extra={
            "trace_id": trace_id,
            "request_id": request_id,
            "event_id": event_id,
            "error_type": "ValidationError",
            "error_message": str(exc),
            "endpoint": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "message": str(exc),
            "trace_id": trace_id,
            "request_id": request_id
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with trace context"""
    trace_id = get_trace_id()
    request_id = get_request_id()
    event_id = get_event_id()
    
    logger.error(
        "Unhandled exception",
        extra={
            "trace_id": trace_id,
            "request_id": request_id,
            "event_id": event_id,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "endpoint": request.url.path
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "trace_id": trace_id,
            "request_id": request_id
        }
    )

def register_exception_handlers(app):
    """Register all exception handlers with the FastAPI app"""
    app.add_exception_handler(EventNotFound, event_not_found_handler)
    app.add_exception_handler(CapacityExceeded, capacity_exceeded_handler)
    app.add_exception_handler(DuplicateRegistration, duplicate_registration_handler)
    app.add_exception_handler(ValidationError, validation_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)
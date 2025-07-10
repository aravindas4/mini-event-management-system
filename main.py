import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from config.logging import setup_logging
from config.app import AppSettings
from app.core.middlewares.trace_context_middleware import TraceContextMiddleware
from app.core.middlewares.request_logging_middleware import RequestLoggingMiddleware
from app.core.exception_handlers import register_exception_handlers

# Load environment variables
load_dotenv()

# Setup logging
app_settings = AppSettings()
setup_logging(app_settings.APP_ENV if hasattr(app_settings, "APP_ENV") else "INFO")

logger = logging.getLogger("event_management.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Mini Event Management System")
    # Startup: Database connection, table creation
    yield
    # Shutdown: Database cleanup
    logger.info("Shutting down Mini Event Management System")


app = FastAPI(
    title="Mini Event Management System",
    description="A simple event management API with attendee registration",
    version="1.0.0",
    lifespan=lifespan,
)

# Register exception handlers
register_exception_handlers(app)

# Add middlewares in the correct order
# TraceContextMiddleware must be first to set context for other middlewares
app.add_middleware(TraceContextMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health-check")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Mini Event Management System"}


# Include routers
from app.events.routes import events_router

app.include_router(events_router)

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True if os.getenv("APP_ENV") == "development" else False,
        log_level="debug" if os.getenv("DEBUG") == "true" else "info",
    )

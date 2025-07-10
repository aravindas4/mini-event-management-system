import logging
import sys


class EventManagementLogFormatter(logging.Formatter):
    """Custom formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        # Add event management context
        if hasattr(record, "event_id"):
            record.msg = f"[event_id={record.event_id}] {record.msg}"
        if hasattr(record, "request_id"):
            record.msg = f"[request_id={record.request_id}] {record.msg}"
        if hasattr(record, "trace_id"):
            record.msg = f"[trace_id={record.trace_id}] {record.msg}"

        return super().format(record)


def setup_logging(log_level: str = "INFO") -> None:
    """Setup application logging"""
    # Map environment names to logging levels
    level_mapping = {
        "DEVELOPMENT": "DEBUG",
        "TESTING": "DEBUG",
        "PRODUCTION": "INFO",
        "DEBUG": "DEBUG",
        "INFO": "INFO",
        "WARNING": "WARNING",
        "ERROR": "ERROR",
    }

    # Get the appropriate logging level
    mapped_level = level_mapping.get(log_level.upper(), "INFO")

    logging.basicConfig(
        level=getattr(logging, mapped_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/app.log", mode="a"),
        ],
    )

    # Set custom formatter
    for handler in logging.getLogger().handlers:
        handler.setFormatter(EventManagementLogFormatter())

"""
Structured logging configuration for UP2D8 Backend API.

Provides JSON-formatted logging with request context for better observability.
This configuration uses Python's built-in logging (no additional costs).
"""

import logging
import sys
from typing import Any, Dict


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs structured JSON-like log entries.

    Each log entry includes:
    - timestamp: ISO format timestamp
    - level: Log level (INFO, ERROR, etc.)
    - logger: Logger name (module path)
    - message: Log message
    - extra: Any additional fields passed to the logger
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON string."""
        import json
        from datetime import datetime, UTC

        # Base log entry
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields (request_id, user_id, etc.)
        # These are added via LoggerAdapter or extra parameter
        extra_fields = {
            k: v for k, v in record.__dict__.items()
            if k not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "message", "pathname", "process", "processName",
                "relativeCreated", "thread", "threadName", "exc_info",
                "exc_text", "stack_info"
            ]
        }

        if extra_fields:
            log_entry["extra"] = extra_fields

        return json.dumps(log_entry)


def configure_logging(log_level: str = "INFO", enable_structured: bool = True) -> None:
    """
    Configure application-wide logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_structured: If True, use structured JSON logging. If False, use simple format.

    Environment Variables:
        LOG_LEVEL: Override log level (default: INFO)
        STRUCTURED_LOGGING: Set to 'false' to disable structured logging (default: true)
    """
    import os

    # Allow environment variable override
    log_level = os.getenv("LOG_LEVEL", log_level).upper()
    enable_structured = os.getenv("STRUCTURED_LOGGING", "true").lower() != "false"

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))

    # Set formatter
    if enable_structured:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Log configuration
    root_logger.info(
        f"Logging configured",
        extra={
            "log_level": log_level,
            "structured_logging": enable_structured
        }
    )


def get_logger_with_context(name: str, **context) -> logging.LoggerAdapter:
    """
    Get a logger with additional context fields.

    Args:
        name: Logger name (usually __name__)
        **context: Additional context fields to include in all log entries

    Returns:
        LoggerAdapter that includes context in all log entries

    Example:
        logger = get_logger_with_context(__name__, service="backend-api", version="1.0.0")
        logger.info("Request processed", extra={"user_id": "123", "duration_ms": 45})
    """
    logger = logging.getLogger(name)
    return logging.LoggerAdapter(logger, context)

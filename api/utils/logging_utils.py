"""
Structured Logging Utility for Agent Forge API

This module provides consistent logging functionality across all components
with support for:
- Correlation IDs to track requests through the system
- Structured JSON format logging for better analysis
- Configurable log levels and destinations
- Standard log fields for all messages
"""

import json
import logging
import os
import sys
import time
import uuid
from contextvars import ContextVar
from typing import Any, Dict, Optional

# Context variable to store the correlation ID for the current execution context
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")

# Default log level from environment or INFO
DEFAULT_LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_TO_JSON = os.environ.get("LOG_TO_JSON", "").lower() == "true"

# Configure standard logging levels
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as a JSON string."""
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line_number": record.lineno,
        }

        # Add correlation ID if available
        correlation_id = correlation_id_var.get()
        if correlation_id:
            log_data["correlation_id"] = correlation_id

        # Add exception info if available
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add any extra attributes
        for key, value in record.__dict__.items():
            if key not in [
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "id",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
            ]:
                log_data[key] = value

        return json.dumps(log_data)


class StructuredLogger:
    """Structured logger with support for correlation IDs and standardized formatting."""

    def __init__(self, name: str, log_level: str = DEFAULT_LOG_LEVEL):
        """Initialize the structured logger.

        Args:
            name: The name of the logger
            log_level: The log level to use (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(LOG_LEVELS.get(log_level, logging.INFO))

        # Remove existing handlers (to avoid duplicates)
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Set up console handler
        console_handler = logging.StreamHandler(sys.stdout)

        # Configure formatter based on environment
        if LOG_TO_JSON:
            formatter = JsonFormatter()
        else:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(correlation_id)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def _add_correlation_id(
        self, extra: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add correlation ID to extra data for logging."""
        if extra is None:
            extra = {}

        correlation_id = correlation_id_var.get()
        if correlation_id:
            extra["correlation_id"] = correlation_id
        else:
            extra["correlation_id"] = "no-correlation-id"

        return extra

    def debug(
        self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info=False
    ):
        """Log a debug message."""
        self.logger.debug(
            message, extra=self._add_correlation_id(extra), exc_info=exc_info
        )

    def info(
        self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info=False
    ):
        """Log an info message."""
        self.logger.info(
            message, extra=self._add_correlation_id(extra), exc_info=exc_info
        )

    def warning(
        self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info=False
    ):
        """Log a warning message."""
        self.logger.warning(
            message, extra=self._add_correlation_id(extra), exc_info=exc_info
        )

    def error(
        self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info=True
    ):
        """Log an error message."""
        self.logger.error(
            message, extra=self._add_correlation_id(extra), exc_info=exc_info
        )

    def critical(
        self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info=True
    ):
        """Log a critical message."""
        self.logger.critical(
            message, extra=self._add_correlation_id(extra), exc_info=exc_info
        )

    def log_request_start(
        self,
        request_id: str,
        method: str,
        path: str,
        client_ip: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ):
        """Log the start of a request."""
        if extra is None:
            extra = {}

        extra.update(
            {
                "event_type": "request_start",
                "request_id": request_id,
                "method": method,
                "path": path,
                "client_ip": client_ip,
                "timestamp": time.time(),
            }
        )

        self.info(f"Starting request {method} {path}", extra=extra)

    def log_request_end(
        self,
        request_id: str,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        extra: Optional[Dict[str, Any]] = None,
    ):
        """Log the end of a request."""
        if extra is None:
            extra = {}

        extra.update(
            {
                "event_type": "request_end",
                "request_id": request_id,
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "timestamp": time.time(),
            }
        )

        # Log at different levels based on status code and duration
        if status_code >= 500:
            self.error(
                f"Request failed {method} {path}: {status_code} in {duration_ms:.2f}ms",
                extra=extra,
            )
        elif status_code >= 400:
            self.warning(
                f"Client error {method} {path}: {status_code} in {duration_ms:.2f}ms",
                extra=extra,
            )
        elif duration_ms > 5000:  # Log slow requests as warnings
            self.warning(
                f"Slow request {method} {path}: {status_code} in {duration_ms:.2f}ms",
                extra=extra,
            )
        else:
            self.info(
                f"Completed request {method} {path}: {status_code} in {duration_ms:.2f}ms",
                extra=extra,
            )

    def log_llm_call(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        duration_ms: float,
        success: bool = True,
        error_type: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ):
        """Log an LLM API call with performance metrics."""
        if extra is None:
            extra = {}

        extra.update(
            {
                "event_type": "llm_call",
                "model": model,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "duration_ms": duration_ms,
                "success": success,
                "error_type": error_type,
                "timestamp": time.time(),
            }
        )

        if success:
            self.info(
                f"LLM call to {model}: {prompt_tokens + completion_tokens} tokens in {duration_ms:.2f}ms",
                extra=extra,
            )
        else:
            self.error(
                f"LLM call to {model} failed: {error_type} after {duration_ms:.2f}ms",
                extra=extra,
            )

    def log_database_operation(
        self,
        operation: str,
        table: Optional[str],
        duration_ms: float,
        rows_affected: Optional[int] = None,
        success: bool = True,
        error_type: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ):
        """Log a database operation with performance metrics."""
        if extra is None:
            extra = {}

        extra.update(
            {
                "event_type": "database_operation",
                "operation": operation,
                "table": table,
                "duration_ms": duration_ms,
                "rows_affected": rows_affected,
                "success": success,
                "error_type": error_type,
                "timestamp": time.time(),
            }
        )

        if success:
            if duration_ms > 1000:  # Log slow queries as warnings
                self.warning(
                    f"Slow DB {operation} on {table}: {rows_affected} rows in {duration_ms:.2f}ms",
                    extra=extra,
                )
            else:
                self.debug(
                    f"DB {operation} on {table}: {rows_affected} rows in {duration_ms:.2f}ms",
                    extra=extra,
                )
        else:
            self.error(
                f"DB {operation} on {table} failed: {error_type} after {duration_ms:.2f}ms",
                extra=extra,
            )

    def log_search_operation(
        self,
        query: str,
        results_count: int,
        duration_ms: float,
        search_type: str = "semantic",
        extra: Optional[Dict[str, Any]] = None,
    ):
        """Log a search operation with performance and quality metrics."""
        if extra is None:
            extra = {}

        # Sanitize query for logging (limit length and remove sensitive data)
        sanitized_query = query[:100] if len(query) > 100 else query

        extra.update(
            {
                "event_type": "search_operation",
                "search_type": search_type,
                "query_length": len(query),
                "results_count": results_count,
                "duration_ms": duration_ms,
                "timestamp": time.time(),
            }
        )

        # Publish custom metrics if available
        try:
            from .custom_metrics import publish_search_metrics

            # Extract search quality metrics from extra data
            intent_detected = extra.get("intent_detected", "unknown")
            intent_confidence = extra.get("intent_confidence", 0.5)
            query_enhanced = extra.get("query_enhanced", False)
            relevance_score = extra.get("average_relevance_score", 0.0)

            publish_search_metrics(
                query=query,
                results_count=results_count,
                duration_ms=duration_ms,
                intent_detected=intent_detected,
                intent_confidence=intent_confidence,
                query_enhanced=query_enhanced,
                relevance_score=relevance_score,
                search_strategy=search_type,
            )
        except ImportError:
            pass  # Custom metrics not available
        except Exception as e:
            # Don't fail logging if metrics publishing fails
            self.debug(f"Failed to publish search metrics: {e}")

        if results_count == 0:
            self.warning(
                f"No results for {search_type} search: '{sanitized_query}' in {duration_ms:.2f}ms",
                extra=extra,
            )
        elif duration_ms > 3000:  # Log slow searches
            self.warning(
                f"Slow {search_type} search: '{sanitized_query}' returned {results_count} results in {duration_ms:.2f}ms",
                extra=extra,
            )
        else:
            self.info(
                f"{search_type.title()} search: '{sanitized_query}' returned {results_count} results in {duration_ms:.2f}ms",
                extra=extra,
            )


def set_correlation_id(correlation_id: Optional[str] = None) -> str:
    """Set the correlation ID for the current execution context.

    Args:
        correlation_id: The correlation ID to use, or None to generate a new one

    Returns:
        The correlation ID that was set
    """
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())

    correlation_id_var.set(correlation_id)
    return correlation_id


def get_correlation_id() -> str:
    """Get the correlation ID for the current execution context.

    Returns:
        The current correlation ID or an empty string if not set
    """
    return correlation_id_var.get()


def get_logger(name: str, log_level: Optional[str] = None) -> StructuredLogger:
    """Get a structured logger with the given name and log level.

    Args:
        name: The name of the logger
        log_level: The log level to use, or None to use the default

    Returns:
        A StructuredLogger instance
    """
    if log_level is None:
        log_level = DEFAULT_LOG_LEVEL

    return StructuredLogger(name, log_level)

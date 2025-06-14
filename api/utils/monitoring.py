"""
Monitoring Utilities for Agent Forge API

This module provides metrics tracking capabilities for the Agent Forge API including:
- API call counts by endpoint and status code
- Response time metrics
- Error rate tracking
- Token usage metrics

It is designed to work alongside the structured logging system and can output metrics
to Google Cloud Monitoring (when deployed) or locally for development.
"""

import json
import os
import threading
import time
from collections import defaultdict
from typing import Any, Dict, Optional

# Import our logging utilities
from .logging_utils import get_correlation_id, get_logger

# Configure logger
logger = get_logger("monitoring")

# Check if we're running in Google Cloud
IN_GCP = os.environ.get("K_SERVICE", "") != ""


# Global metrics store for local development
# In production, these would be reported to Google Cloud Monitoring
class MetricsStore:
    """In-memory metrics store for local development."""

    def __init__(self):
        self.metrics = defaultdict(lambda: defaultdict(int))
        self.timers = {}
        self.lock = threading.Lock()

    def increment(
        self, metric_name: str, value: int = 1, labels: Optional[Dict[str, str]] = None
    ):
        """Increment a counter metric."""
        with self.lock:
            key = metric_name
            if labels:
                # Convert labels to a string for use as a key
                label_str = json.dumps(labels, sort_keys=True)
                key = f"{metric_name}:{label_str}"
            self.metrics[key]["value"] += value
            if labels:
                self.metrics[key]["labels"] = labels

    def set_value(
        self, metric_name: str, value: float, labels: Optional[Dict[str, str]] = None
    ):
        """Set a gauge metric value."""
        with self.lock:
            key = metric_name
            if labels:
                # Convert labels to a string for use as a key
                label_str = json.dumps(labels, sort_keys=True)
                key = f"{metric_name}:{label_str}"
            self.metrics[key]["value"] = value
            if labels:
                self.metrics[key]["labels"] = labels

    def start_timer(self, timer_id: str):
        """Start a timer for measuring durations."""
        self.timers[timer_id] = time.time()

    def stop_timer(
        self, timer_id: str, metric_name: str, labels: Optional[Dict[str, str]] = None
    ) -> float:
        """Stop a timer and record the duration as a metric."""
        if timer_id not in self.timers:
            logger.warning(f"Timer {timer_id} not found")
            return 0.0

        duration = time.time() - self.timers.pop(timer_id)
        duration_ms = duration * 1000

        self.set_value(metric_name, duration_ms, labels)
        return duration_ms

    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics as a dictionary."""
        with self.lock:
            # Create a regular dict to avoid defaultdict serialization issues
            return dict(self.metrics)


# Create a global metrics store
metrics_store = MetricsStore()


# API Metrics Functions
def track_api_call(endpoint: str, method: str, status_code: int):
    """Track an API call.

    Args:
        endpoint: The API endpoint path
        method: The HTTP method (GET, POST, etc.)
        status_code: The HTTP status code
    """
    # Track total calls
    metrics_store.increment(
        "api_calls_total",
        labels={
            "endpoint": endpoint,
            "method": method,
        },
    )

    # Track calls by status code
    metrics_store.increment(
        "api_calls_by_status",
        labels={
            "endpoint": endpoint,
            "method": method,
            "status_code": str(status_code),
        },
    )

    # Track errors (4xx and 5xx status codes)
    if status_code >= 400:
        metrics_store.increment(
            "api_errors_total",
            labels={
                "endpoint": endpoint,
                "method": method,
                "status_code": str(status_code),
            },
        )


def start_request_timer() -> str:
    """Start a timer for tracking request duration.

    Returns:
        str: The timer ID
    """
    # Use correlation ID for timer ID to tie it to the request
    timer_id = get_correlation_id()
    metrics_store.start_timer(timer_id)
    return timer_id


def stop_request_timer(timer_id: str, endpoint: str, method: str) -> float:
    """Stop a request timer and record the duration.

    Args:
        timer_id: The timer ID returned by start_request_timer
        endpoint: The API endpoint path
        method: The HTTP method

    Returns:
        float: The request duration in milliseconds
    """
    return metrics_store.stop_timer(
        timer_id,
        "api_request_duration_ms",
        labels={
            "endpoint": endpoint,
            "method": method,
        },
    )


# LLM Usage Metrics
def track_token_usage(num_prompt_tokens: int, num_completion_tokens: int, model: str):
    """Track token usage for an LLM call.

    Args:
        num_prompt_tokens: Number of tokens in the prompt
        num_completion_tokens: Number of tokens in the completion
        model: The LLM model used
    """
    # Track prompt tokens
    metrics_store.increment(
        "llm_prompt_tokens_total", value=num_prompt_tokens, labels={"model": model}
    )

    # Track completion tokens
    metrics_store.increment(
        "llm_completion_tokens_total",
        value=num_completion_tokens,
        labels={"model": model},
    )

    # Track total tokens
    metrics_store.increment(
        "llm_tokens_total",
        value=num_prompt_tokens + num_completion_tokens,
        labels={"model": model},
    )


def track_llm_call(model: str, success: bool = True, error_type: Optional[str] = None):
    """Track an LLM API call.

    Args:
        model: The LLM model used
        success: Whether the call was successful
        error_type: The type of error if the call failed
    """
    # Track total calls
    metrics_store.increment("llm_calls_total", labels={"model": model})

    # Track successful calls
    if success:
        metrics_store.increment("llm_success_total", labels={"model": model})
    else:
        # Track failed calls
        metrics_store.increment(
            "llm_errors_total",
            labels={"model": model, "error_type": error_type or "unknown"},
        )


def start_llm_timer() -> str:
    """Start a timer for tracking LLM call duration.

    Returns:
        str: The timer ID
    """
    timer_id = f"llm_{get_correlation_id()}"
    metrics_store.start_timer(timer_id)
    return timer_id


def stop_llm_timer(timer_id: str, model: str) -> float:
    """Stop an LLM timer and record the duration.

    Args:
        timer_id: The timer ID returned by start_llm_timer
        model: The LLM model used

    Returns:
        float: The LLM call duration in milliseconds
    """
    return metrics_store.stop_timer(
        timer_id, "llm_request_duration_ms", labels={"model": model}
    )


# Database Metrics
def track_db_call(
    operation: str, success: bool = True, error_type: Optional[str] = None
):
    """Track a database operation.

    Args:
        operation: The database operation (e.g., "query", "insert")
        success: Whether the operation was successful
        error_type: The type of error if the operation failed
    """
    # Track total calls
    metrics_store.increment("db_calls_total", labels={"operation": operation})

    # Track successful calls
    if success:
        metrics_store.increment("db_success_total", labels={"operation": operation})
    else:
        # Track failed calls
        metrics_store.increment(
            "db_errors_total",
            labels={"operation": operation, "error_type": error_type or "unknown"},
        )


def start_db_timer() -> str:
    """Start a timer for tracking database operation duration.

    Returns:
        str: The timer ID
    """
    timer_id = f"db_{get_correlation_id()}"
    metrics_store.start_timer(timer_id)
    return timer_id


def stop_db_timer(timer_id: str, operation: str) -> float:
    """Stop a database timer and record the duration.

    Args:
        timer_id: The timer ID returned by start_db_timer
        operation: The database operation

    Returns:
        float: The database operation duration in milliseconds
    """
    return metrics_store.stop_timer(
        timer_id, "db_operation_duration_ms", labels={"operation": operation}
    )


# User metrics
def track_unique_user(user_id: str):
    """Track a unique user.

    Args:
        user_id: The user ID
    """
    # Privacy enhancement: Only store the last 4 characters of the user ID for tracking
    # This prevents exposing full IDs in metrics while still allowing for uniqueness monitoring
    private_id = user_id[-4:] if len(user_id) > 4 else "user"

    # Log at debug level with privacy-conscious ID
    logger.debug(f"Tracked unique user with ID ending in: {private_id}")

    # Track total unique users (this counts each hit, not truly unique)
    metrics_store.increment("unique_users_total")

    # FUTURE ENHANCEMENT: Could use a set to track truly unique users
    # but would need to be mindful of memory usage in a long-running server


def track_user_credits(user_id: str, credits: int):
    """Track a user's credit balance.

    Args:
        user_id: The user ID
        credits: The user's current credit balance
    """
    # Aggregate metrics without exposing user IDs
    metrics_store.increment("users_with_credits", value=1)

    # Track total credits across all users
    metrics_store.increment("total_credits", value=credits)

    # For average calculations, we can store a separate metric
    metrics_store.set_value(
        "avg_credits_per_user",
        credits,  # This is not a true average, but a simple placeholder
    )

    # Log the credit update for debugging
    logger.debug(
        f"User (ID ending in {user_id[-4:] if len(user_id) > 4 else '****'}) has {credits} credits"
    )


# Expose metrics for monitoring systems
def get_metrics_json() -> str:
    """Get all metrics as a JSON string.

    Returns:
        str: JSON string representation of metrics
    """
    try:
        # Get metrics from store
        metrics = metrics_store.get_metrics()

        # Custom JSON encoder to handle special types
        class EnhancedJSONEncoder(json.JSONEncoder):
            def default(self, obj):
                # Handle bytes
                if isinstance(obj, bytes):
                    return obj.decode("utf-8", errors="replace")
                # Handle datetime objects
                elif hasattr(obj, "isoformat"):
                    return obj.isoformat()
                # Handle UUID objects
                elif hasattr(obj, "hex"):
                    return str(obj)
                # Handle any object with __str__ method
                elif hasattr(obj, "__str__"):
                    return str(obj)
                return super().default(obj)

        # Convert to JSON string with custom encoder
        return json.dumps(metrics, cls=EnhancedJSONEncoder)
    except Exception as e:
        logger.error(f"Error serializing metrics: {e}")
        # Return empty JSON object on error
        return "{}"


def reset_metrics():
    """Reset all metrics (for testing)."""
    metrics_store.metrics.clear()
    metrics_store.timers.clear()


# Integration with Google Cloud Monitoring (stub implementation)
def export_metrics_to_gcp():
    """Export metrics to Google Cloud Monitoring.

    This function exports collected metrics to Google Cloud Monitoring as custom metrics.
    It converts our internal metrics format to the format expected by Cloud Monitoring.
    """
    if not IN_GCP:
        logger.debug("Not running in GCP, skipping metrics export")
        return

    try:
        import datetime

        from google.cloud import monitoring_v3

        # from google.api import metric_pb2 # Removed unused import
        # from google.api import label_pb2 # Removed unused import
        from google.protobuf import timestamp_pb2

        # Get metrics from store
        metrics = metrics_store.get_metrics()

        # Setup client
        client = monitoring_v3.MetricServiceClient()
        project_id = os.environ.get(
            "VERTEX_PROJECT_ID", os.environ.get("GCP_PROJECT_ID")
        )

        if not project_id:
            logger.error("Missing GCP project ID for metrics export")
            return

        project_name = f"projects/{project_id}"

        # Get current time
        now = datetime.datetime.utcnow()
        seconds = int(now.timestamp())
        nanos = int((now.timestamp() - seconds) * 10**9)
        timestamp = timestamp_pb2.Timestamp(seconds=seconds, nanos=nanos)

        # Process and send each metric
        for metric_name, metric_data in metrics.items():
            # Skip complex metrics or ones that can't be easily represented in Cloud Monitoring
            if isinstance(metric_data, dict) and all(
                isinstance(v, (int, float)) for v in metric_data.values()
            ):
                # Process counter metrics
                metric_type = f"custom.googleapis.com/agent_forge/{metric_name}"

                for label_str, value in metric_data.items():
                    # Parse labels
                    label_dict = {}
                    if label_str != "default":
                        try:
                            # Convert from our string format to dict
                            label_parts = label_str.split("|")
                            for part in label_parts:
                                if "=" in part:
                                    k, v = part.split("=", 1)
                                    label_dict[k] = v
                        except Exception as e:
                            logger.warning(
                                f"Error parsing metric labels '{label_str}': {e}"
                            )

                    # Create time series data
                    series = monitoring_v3.TimeSeries()
                    series.metric.type = metric_type

                    # Add labels to metric
                    for k, v in label_dict.items():
                        series.metric.labels[k] = str(v)

                    # Add resource
                    series.resource.type = "global"

                    # Create data point
                    point = monitoring_v3.Point()

                    # Ensure timestamps are properly set with error handling
                    try:
                        # Add end_time to interval - use the CopyFrom method instead of direct assignment
                        point.interval.end_time.CopyFrom(timestamp)
                    except Exception as e:
                        logger.error(
                            f"Error setting timestamp for metric {metric_name}: {e}"
                        )
                        # Create a new timestamp if there was an issue
                        now = datetime.datetime.utcnow()
                        seconds = int(now.timestamp())
                        nanos = int((now.timestamp() - seconds) * 10**9)
                        new_timestamp = timestamp_pb2.Timestamp(
                            seconds=seconds, nanos=nanos
                        )
                        point.interval.end_time.CopyFrom(new_timestamp)

                    # Handle int vs float
                    if isinstance(value, int):
                        point.value.int64_value = value
                    else:
                        point.value.double_value = value

                    series.points.append(point)

                    # Write time series data
                    try:
                        client.create_time_series(
                            name=project_name, time_series=[series]
                        )
                        logger.debug(
                            f"Exported metric {metric_name} to Google Cloud Monitoring"
                        )
                    except Exception as e:
                        logger.error(
                            f"Error exporting metric {metric_name} to GCP: {e}"
                        )

        logger.info(
            f"Successfully exported {len(metrics)} metrics to Google Cloud Monitoring"
        )

    except ImportError as e:
        logger.error(f"Google Cloud Monitoring libraries not installed: {e}")
    except Exception as e:
        logger.error(f"Error exporting metrics to GCP: {e}")


# Optional periodic export functionality (for production)
def start_metrics_export(interval_seconds: int = 60):
    """Start periodic export of metrics to monitoring systems.

    Args:
        interval_seconds: Export interval in seconds
    """

    def export_loop():
        while True:
            time.sleep(interval_seconds)
            try:
                export_metrics_to_gcp()
            except Exception as e:
                logger.error(f"Error exporting metrics: {e}")


# Direct Orchestrator Monitoring Functions
def track_orchestrator_session(session_id: str, total_events: int):
    """Track the start of a Direct Orchestrator session."""
    metrics_store.increment(
        "orchestrator_sessions_total", labels={"session_id": session_id[:50]}
    )

    metrics_store.set_value(
        "orchestrator_events_planned",
        total_events,
        labels={"session_id": session_id[:50]},
    )

    logger.info(
        f"📊 Started tracking orchestrator session: {session_id} ({total_events} events)"
    )


def track_orchestrator_event_completion(
    session_id: str,
    success: bool,
    completeness_score: float,
    processing_time: float,
    speakers_count: int,
    sponsors_count: int,
    images_analyzed: int,
):
    """Track completion of a single event in orchestrator."""
    status = "success" if success else "failed"

    # Track event completion
    metrics_store.increment(
        "orchestrator_events_processed",
        labels={"session_id": session_id[:50], "status": status},
    )

    if success:
        # Track quality metrics for successful events
        metrics_store.set_value(
            "orchestrator_completeness_score",
            completeness_score * 100,  # Convert to percentage
            labels={"session_id": session_id[:50]},
        )

        metrics_store.set_value(
            "orchestrator_processing_time_ms",
            processing_time * 1000,  # Convert to milliseconds
            labels={"session_id": session_id[:50]},
        )

        # Track extraction results
        metrics_store.set_value(
            "orchestrator_speakers_extracted",
            speakers_count,
            labels={"session_id": session_id[:50]},
        )

        metrics_store.set_value(
            "orchestrator_sponsors_extracted",
            sponsors_count,
            labels={"session_id": session_id[:50]},
        )

        metrics_store.set_value(
            "orchestrator_images_analyzed",
            images_analyzed,
            labels={"session_id": session_id[:50]},
        )


def track_orchestrator_session_completion(
    session_id: str,
    total_events: int,
    successful_events: int,
    failed_events: int,
    avg_completeness: float,
    avg_processing_time: float,
    total_speakers: int,
    total_sponsors: int,
):
    """Track completion of a full orchestrator session."""
    success_rate = (successful_events / total_events * 100) if total_events > 0 else 0

    # Track session completion metrics
    metrics_store.set_value(
        "orchestrator_session_success_rate",
        success_rate,
        labels={"session_id": session_id[:50]},
    )

    metrics_store.set_value(
        "orchestrator_session_avg_completeness",
        avg_completeness,
        labels={"session_id": session_id[:50]},
    )

    metrics_store.set_value(
        "orchestrator_session_avg_processing_time",
        avg_processing_time,
        labels={"session_id": session_id[:50]},
    )

    metrics_store.set_value(
        "orchestrator_session_total_speakers",
        total_speakers,
        labels={"session_id": session_id[:50]},
    )

    metrics_store.set_value(
        "orchestrator_session_total_sponsors",
        total_sponsors,
        labels={"session_id": session_id[:50]},
    )

    # Track overall orchestrator performance
    metrics_store.increment("orchestrator_sessions_completed")
    metrics_store.increment("orchestrator_total_events_processed", value=total_events)
    metrics_store.increment(
        "orchestrator_total_successful_events", value=successful_events
    )

    logger.info(
        f"📊 Completed orchestrator session: {session_id} - "
        f"{success_rate:.1f}% success rate, {avg_completeness:.1f}% avg completeness"
    )


def track_orchestrator_error(
    session_id: str, error_message: str, event_url: str = None
):
    """Track an error during orchestrator processing."""
    metrics_store.increment(
        "orchestrator_errors_total",
        labels={"session_id": session_id[:50], "error_type": "processing_error"},
    )

    if event_url:
        logger.error(
            f"🚨 Orchestrator error in session {session_id} for {event_url}: {error_message}"
        )
    else:
        logger.error(f"🚨 Orchestrator error in session {session_id}: {error_message}")


def start_orchestrator_timer() -> str:
    """Start a timer for orchestrator operations."""
    timer_id = f"orchestrator_{int(time.time() * 1000000)}"
    return metrics_store.start_timer(timer_id)


def stop_orchestrator_timer(timer_id: str, operation: str) -> float:
    """Stop an orchestrator timer and record the duration."""
    return metrics_store.stop_timer(
        timer_id,
        f"orchestrator_{operation}_duration_ms",
        labels={"operation": operation},
    )

    # Start export thread if in production
    if IN_GCP:
        export_thread = threading.Thread(target=export_loop, daemon=True)
        export_thread.start()
        logger.info(f"Started metrics export thread (interval: {interval_seconds}s)")
    else:
        logger.debug("Not running in GCP, metrics export not started")

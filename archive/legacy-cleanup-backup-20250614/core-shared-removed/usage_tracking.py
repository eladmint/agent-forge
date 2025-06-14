"""
Usage tracking and analytics logging functionality.
"""

import asyncio
import datetime
import json
import logging
import uuid
from datetime import UTC
from typing import Any, Dict, Optional

from supabase import Client as SupabaseClient
from supabase import PostgrestAPIError

logger = logging.getLogger(__name__)


async def log_usage(
    request,
    processing_time_ms: int,
    status: str,
    error_type: Optional[str] = None,
    query_type: Optional[str] = None,  # Make optional if not always available
    function_called: Optional[str] = None,
    function_success: Optional[bool] = None,
    debug_info: Optional[Dict[str, Any]] = None,
    db: SupabaseClient = None,  # Pass the DB client directly
) -> None:
    """
    Logs usage and performance metrics to the usage_tracking table.
    Handles potential database errors gracefully.
    """
    if not db:
        logger.error(
            "log_usage called without a valid database client. Skipping logging."
        )
        return

    log_entry = {
        "id": str(uuid.uuid4()),  # Generate UUID for the log entry
        "user_id": request.user_id if hasattr(request, "user_id") else "unknown",
        "query": request.message if hasattr(request, "message") else "unknown",
        "timestamp": datetime.datetime.now(UTC).isoformat(),
        "processing_time_ms": processing_time_ms,
        "status": status,
        "error_type": error_type,
        "query_type": query_type if query_type else "unknown",  # Handle potential None
        "function_called": function_called,
        "function_success": function_success,
        "debug_info": (
            json.dumps(debug_info, default=str) if debug_info else None
        ),  # Serialize debug info
    }

    try:
        logger.info(
            f"Logging usage: User={log_entry['user_id']}, Status={status}, Time={processing_time_ms}ms, Func={function_called}, FuncSuccess={function_success}, QType={query_type}, ErrType={error_type}"
        )
        # Use await with insert as it's likely an async operation under the hood
        # This assumes supabase-py's insert/execute might be async
        # If it blocks, consider asyncio.to_thread if necessary
        response = await asyncio.to_thread(
            db.table("usage_tracking").insert(log_entry).execute
        )
        # Check for errors in the response object (adjust based on actual response structure)
        if hasattr(response, "error") and response.error:
            logger.error(f"Error logging usage to Supabase: {response.error}")
        elif hasattr(response, "status_code") and response.status_code >= 400:
            logger.error(
                f"Error logging usage to Supabase: HTTP {response.status_code}"
            )
        else:
            logger.debug("Usage logged successfully to Supabase.")

    except PostgrestAPIError as pe:
        logger.error(
            f"PostgrestAPIError logging usage: Code={pe.code}, Message={pe.message}",
            exc_info=False,  # Don't need full traceback for known API errors
        )
    except Exception as e:
        logger.error(f"Unexpected error logging usage: {e}", exc_info=True)

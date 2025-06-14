"""
Database utilities package for Agent Forge.

This package provides modular database functionality split across focused modules:
- client: Supabase client initialization and connection management
- social_links: Social media link extraction and processing
- event_data: Event data saving and processing logic
- search: Search and query functionality (keyword search, date queries, speaker lookup)
- usage_tracking: Usage tracking and analytics logging
- utils: Database utilities and helper functions
"""

# Import main functions for backward compatibility
from .client import get_supabase_client, init_supabase_client
from .event_data import save_event_data
from .search import (
    _sync_get_events_by_date,
    _sync_get_speaker_by_name,
    _sync_keyword_search_events,
)
from .social_links import extract_social_links
from .usage_tracking import log_usage
from .utils import _create_iso_timestamp, _sync_insert, _sync_upsert

__all__ = [
    # Client management
    "init_supabase_client",
    "get_supabase_client",
    # Social links
    "extract_social_links",
    # Event data
    "save_event_data",
    # Search functionality
    "_sync_get_speaker_by_name",
    "_sync_get_events_by_date",
    "_sync_keyword_search_events",
    # Usage tracking
    "log_usage",
    # Database utilities
    "_sync_upsert",
    "_sync_insert",
    "_create_iso_timestamp",
]

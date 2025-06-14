"""
Supabase client initialization and connection management.
"""

import logging
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from supabase import Client as SupabaseClient
from supabase import create_client

# Load environment variables
load_dotenv()

# Initialize logging
logger = logging.getLogger(__name__)

# Global variable to hold the Supabase client instance
supabase_client: Optional[SupabaseClient] = None

# Constants for database interactions
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


def init_supabase_client():
    """
    Initializes the Supabase client using environment variables.
    """
    global supabase_client
    if supabase_client is None:
        logger.info(
            "Attempting to initialize Supabase client (called from dependency/getter)..."
        )
        try:
            # <<< ADDED LOGGING >>>
            logger.info(
                "init_supabase_client: About to read SUPABASE_URL and SUPABASE_KEY from environment or files."
            )
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")

            # If environment variables are not set, try reading from mounted files
            if not supabase_url:
                url_file_path = Path("/etc/secrets/supabase-url/url")
                if url_file_path.is_file():
                    try:
                        supabase_url = url_file_path.read_text().strip()
                        logger.info(f"Read SUPABASE_URL from file: {url_file_path}")
                    except Exception as e:
                        logger.error(
                            f"Failed to read SUPABASE_URL from file {url_file_path}: {e}"
                        )
                else:
                    logger.warning(
                        f"SUPABASE_URL env var not set and file not found at {url_file_path}"
                    )

            if not supabase_key:
                key_file_path = Path("/etc/secrets/supabase-key/key")
                if key_file_path.is_file():
                    try:
                        supabase_key = key_file_path.read_text().strip()
                        logger.info(f"Read SUPABASE_KEY from file: {key_file_path}")
                    except Exception as e:
                        logger.error(
                            f"Failed to read SUPABASE_KEY from file {key_file_path}: {e}"
                        )
                else:
                    logger.warning(
                        f"SUPABASE_KEY env var not set and file not found at {key_file_path}"
                    )

            # <<< ADDED LOGGING >>>
            logger.info(
                f"init_supabase_client: Read SUPABASE_URL. Is None? {supabase_url is None}. Type: {type(supabase_url)}"
            )
            logger.info(
                f"init_supabase_client: Read SUPABASE_KEY. Is None? {supabase_key is None}. Type: {type(supabase_key)}"
            )

            if not supabase_url or not supabase_key:
                # Updated error message to reflect source
                logger.error(
                    "Supabase URL or Key not found in environment variables or mounted secret files."
                )
                raise ValueError(
                    "Supabase URL or Key not found in environment variables or mounted secret files."
                )
            # Use the same initialization approach as main.py for consistency
            supabase_client = create_client(supabase_url, supabase_key)
            logger.info("Supabase client initialized successfully.")
        except ValueError as ve:  # Keep specific error logging
            logger.error(f"Value error during Supabase init: {ve}")
            raise
        except Exception as e:
            logger.error(
                f"Failed to initialize Supabase client: {e}", exc_info=True
            )  # Add exc_info
            raise
    else:
        logger.info("Supabase client already initialized.")

    return supabase_client


def get_supabase_client() -> SupabaseClient:
    """
    Returns the initialized Supabase client. Initializes it if not already done.
    """
    # This function now IS the primary way to get/init the client
    if not supabase_client:
        logger.info(
            "get_supabase_client: Client not found, calling init_supabase_client..."
        )
        return init_supabase_client()
    logger.info("get_supabase_client: Returning existing client instance.")
    return supabase_client

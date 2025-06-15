"""File system utility functions."""

import logging
import os
from typing import Optional

# Standard logger for the module
logger = logging.getLogger(__name__)


def ensure_directory_exists(
    dir_path: str, custom_logger: Optional[logging.Logger] = None
) -> bool:
    """Ensures that a directory exists at the specified path.

    If the directory does not exist, this function attempts to create it,
    including any necessary parent directories.

    Args:
        dir_path: The file system path for the directory.
        custom_logger: An optional custom logger instance. If not provided,
                       the module-level logger is used.

    Returns:
        bool: True if the directory exists or was successfully created.
              False if the path is empty, points to an existing file (not a directory),
              or if directory creation fails due to an OSError.

    Side Effects:
        - Creates a directory (and any parent directories) if it doesn't exist.
        - Logs information about its operations (debug, info, warning, error).
    """
    log = custom_logger or logger  # Use provided logger or default to module logger

    if not dir_path:
        log.warning("Cannot ensure directory existence for an empty path.")
        return False

    if os.path.exists(dir_path):
        if os.path.isdir(dir_path):
            log.debug("Directory already exists: %s", dir_path)
            return True
        else:
            # Path exists but is a file or other non-directory type
            log.error("Path exists but is not a directory: %s", dir_path)
            return False
    else:
        # Directory does not exist, attempt to create it
        try:
            # os.makedirs creates parent directories as needed (like mkdir -p)
            # exist_ok=True means it won't raise an error if the directory is created
            # by another process between the os.path.exists check and this call.
            os.makedirs(dir_path, exist_ok=True)
            log.info("Successfully created directory: %s", dir_path)
            return True
        except OSError as e:
            # Catch potential errors during directory creation (e.g., permission issues)
            log.error("Error creating directory %s: %s", dir_path, e, exc_info=True)
            return False

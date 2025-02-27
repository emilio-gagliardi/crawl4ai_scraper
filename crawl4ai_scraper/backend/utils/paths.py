"""Utility functions for working with paths."""

import logging
import os
import sys
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    """
    Get the absolute path to the project root directory by finding
    the top-level project directory.
    """
    # Start from the current file
    current_path = Path(__file__).resolve()

    # Get the project name from environment variable, default to 'crawl4ai_scraper'
    project_name = os.getenv("PROJECT_NAME", "crawl4ai_scraper")

    # Navigate up until we find the top-level project directory
    for parent in [current_path, *current_path.parents]:
        # Check if this is the top-level project directory
        if (
            parent.name == project_name
            and not (parent.parent / project_name).exists()
        ):
            return parent

    # If we couldn't find it, use a fallback approach
    for parent in [current_path, *current_path.parents]:
        # Check for markers that indicate we're at the project root
        if (
            (parent / "dev.env").exists()
            or (parent / ".env").exists()
            or (parent / "run.py").exists()
        ):
            return parent

    # If all else fails, return the directory containing this file
    return current_path.parent.parent.parent.parent


def get_data_dir() -> Path:
    """Get the path to the data directory."""
    return get_project_root() / "data"


def get_downloads_dir() -> Path:
    """Get the path to the downloads directory."""
    return get_data_dir() / "downloads"


def get_logs_dir() -> Path:
    """Get the path to the logs directory."""
    return get_data_dir() / "logs"


def get_temp_dir() -> Path:
    """Get the path to the temporary directory."""
    return get_data_dir() / "temp"


def get_config_dir() -> Path:
    """Get the path to the config directory."""
    return get_data_dir() / "config"


def ensure_dir_exists(path: Path) -> Path:
    """
    Ensure that a directory exists, creating it if necessary.

    Args:
        path: The path to the directory

    Returns:
        Path: The path to the directory
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


# Ensure that all required directories exist
ensure_dir_exists(get_data_dir())
ensure_dir_exists(get_downloads_dir())
ensure_dir_exists(get_logs_dir())
ensure_dir_exists(get_temp_dir())
ensure_dir_exists(get_config_dir())

"""
Environment configuration for the Crawl4AI Scraper application.

This file defines which environment the application is running in
and handles loading the appropriate environment variables.
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

# Set the environment here
# Options: 'dev' or 'prod'
ENVIRONMENT = 'dev'

# Configure logging
logging.basicConfig(level=logging.INFO)
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
    return current_path.parent


def get_env_file_path(env: str) -> Path:
    """Get the path to the environment file based on the environment."""
    env_file = "dev.env" if env == "dev" else ".env"
    return get_project_root() / env_file


def get_environment() -> str:
    """
    Get the current environment setting.

    Checks in this order:
    1. ENV environment variable
    2. ENVIRONMENT variable in this module

    Returns:
        str: The environment name ('dev' or 'prod')
    """
    # First check environment variable
    env = os.getenv("ENV")
    if env:
        return env

    # Then use the ENVIRONMENT variable from this file
    return ENVIRONMENT


def load_environment():
    """Load environment variables based on the current environment."""
    # Get the environment
    env = get_environment()

    # Set it in the environment so other modules can access it
    os.environ["ENV"] = env

    logger.info(f"Loading environment: {env}")

    # Get environment file path
    env_path = get_env_file_path(env)

    # Clear existing environment variables
    for var in [
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_DB",
        "POSTGRES_HOST",
        "POSTGRES_PORT",
    ]:
        if var in os.environ:
            del os.environ[var]

    # Load environment variables with override
    load_dotenv(env_path, override=True)
    logger.info(f"Loaded environment from: {env_path}")

    # Return the environment and path for reference
    return env, env_path


# Load environment when this module is imported
ENV, ENV_PATH = load_environment()

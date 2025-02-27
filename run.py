"""
Run script for Crawl4AI Scraper.

This script provides a convenient way to start the FastAPI application
using uvicorn with the appropriate settings.
"""

import argparse
import logging
import os
import re
import socket
import sys
from pathlib import Path

import uvicorn

# Import environment first to ensure variables are loaded
# This must happen before importing any application modules
import environment

# Add the project root to the Python path to allow importing from the package
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

print(f"Running in {environment.ENV} environment")
print(f"Environment loaded from: {environment.ENV_PATH}")


def get_default_port():
    """
    Get the default port from environment variables.

    First checks for API_PORT, then parses API_URL if available.

    Returns:
        int: The port number (defaults to 8002 if not found)
    """
    # Check if API_PORT is defined
    if 'API_PORT' in os.environ:
        return int(os.environ['API_PORT'])

    # Check if API_URL is defined and try to extract port
    if 'API_URL' in os.environ:
        api_url = os.environ['API_URL']
        port_match = re.search(r':(\d+)', api_url)
        if port_match:
            return int(port_match.group(1))

    # Default port if not found in environment
    return 8002


def update_port_in_environment(port):
    """
    Update the port in environment variables.

    Args:
        port (int): The port number to set
    """
    # Update API_PORT if it exists
    os.environ['API_PORT'] = str(port)

    # Update API_URL if it exists
    if 'API_URL' in os.environ:
        api_url = os.environ['API_URL']
        new_api_url = re.sub(r':\d+', f':{port}', api_url)
        os.environ['API_URL'] = new_api_url
        logger.info(f"Updated API_URL to {new_api_url}")


def is_port_in_use(port):
    """
    Check if a port is in use using Python's socket library.

    Args:
        port (int): The port to check

    Returns:
        bool: True if the port is in use, False otherwise
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return False  # Port is available
        except socket.error:
            return True  # Port is in use


def check_port_and_exit_if_in_use(port):
    """
    Check if the port is available and exit if it's in use.

    Args:
        port (int): The port to check
    """
    logger.info(f"Checking availability of port {port}...")
    if is_port_in_use(port):
        logger.error(f"Port {port} is already in use by another process")
        logger.error(
            "Please choose a different port or stop the process using this"
            " port"
        )
        sys.exit(1)
    else:
        logger.info(f"Port {port} is available")


# Check if we're being run directly or imported by uvicorn
# If we're imported by uvicorn, we need to check the port
if 'uvicorn' in sys.modules:
    # When running through uvicorn, skip the port check
    # This avoids a race condition where we detect our own process
    logger.info("Running through uvicorn, skipping port check")
    # Don't do anything else here
else:
    # Only check port if we're not being run through uvicorn
    # Try to get the port from command line arguments
    port = get_default_port()
    for i, arg in enumerate(sys.argv):
        if arg == '--port' and i + 1 < len(sys.argv):
            try:
                port = int(sys.argv[i + 1])
                break
            except (ValueError, IndexError):
                pass

    # Check if the port is available
    check_port_and_exit_if_in_use(port)


# Import the app after environment is loaded and port is checked
from crawl4ai_scraper.main import app  # noqa: E402

if __name__ == "__main__":
    # Get the default port from environment
    default_port = get_default_port()
    logger.info(f"Default port from environment: {default_port}")

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Run the Crawl4AI Scraper application'
    )
    parser.add_argument(
        '--env',
        type=str,
        default=None,
        choices=['dev', 'prod'],
        help='Environment to run the application in (dev or prod)',
    )
    parser.add_argument(
        '--port',
        type=int,
        default=default_port,
        help=f'Port to run the application on (default: {default_port})',
    )
    args = parser.parse_args()
    logger.info(f"Command line arguments: {args}")

    # Set the environment variable if specified on command line
    if args.env:
        os.environ["ENV"] = args.env
        # Reload environment with new ENV value
        environment.ENV, environment.ENV_PATH = environment.load_environment()
        print(f"Environment changed to: {environment.ENV}")
        print(f"Environment loaded from: {environment.ENV_PATH}")

    # Update port in environment if custom port is provided
    port = args.port
    if port != default_port:
        update_port_in_environment(port)
        print(f"Port changed to: {port}")

    # Check if the port is available
    check_port_and_exit_if_in_use(port)

    # Start the application
    logger.info(f"Starting application on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)

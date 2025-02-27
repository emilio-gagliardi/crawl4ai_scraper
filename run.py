"""
Run script for Crawl4AI Scraper.

This script provides a convenient way to start the FastAPI application
using uvicorn with the appropriate settings.
"""

import argparse
import logging
import os
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

# Import app after environment is loaded - expose it at module level for direct import
# This ensures that all modules imported by main.py will have access to the environment variables
from crawl4ai_scraper.main import app  # noqa: E402

if __name__ == "__main__":
    # Only parse arguments when run directly
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
    args = parser.parse_args()

    # Set the environment variable if specified on command line
    if args.env:
        os.environ["ENV"] = args.env
        # Reload environment with new ENV value
        environment.ENV, environment.ENV_PATH = environment.load_environment()
        print(f"Environment changed to: {environment.ENV}")
        print(f"Environment loaded from: {environment.ENV_PATH}")

    uvicorn.run(app, host="0.0.0.0", port=8002, reload=True)

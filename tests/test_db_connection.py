"""
Simple script to test database connection directly.
"""

import logging
import os
import sys

from dotenv import load_dotenv
from sqlalchemy import text
from sqlmodel import Session, create_engine, select

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get database connection parameters from environment variables
DB_USER = os.getenv("POSTGRES_USER", "crawl4ai")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "your_secure_password_here")
DB_NAME = os.getenv("POSTGRES_DB", "crawl4ai")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5434")

# Build the database URL from environment variables
DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Log the database URL (with password masked)
masked_url = (
    DATABASE_URL.replace(DB_PASSWORD, "********")
    if DB_PASSWORD in DATABASE_URL
    else DATABASE_URL
)
logger.info(f"Connecting to database: {masked_url}")

if __name__ == "__main__":
    try:
        # Create engine
        logger.info("Creating database engine...")
        engine = create_engine(DATABASE_URL, echo=True)

        # Test connection
        logger.info("Testing database connection...")
        with Session(engine) as session:
            # Try a simple query
            result = session.exec(text("SELECT 1")).first()
            logger.info(f"Database connection test successful: {result}")

        logger.info("All tests completed successfully!")

    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        import traceback

        logger.error(f"Exception traceback: {traceback.format_exc()}")
        sys.exit(1)

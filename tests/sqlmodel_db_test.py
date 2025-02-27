"""
SQLModel database connection test.
"""

import logging
import os

from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine, select

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Database connection parameters
DB_USER = "crawl4ai"
DB_PASSWORD = "your_secure_password_here"
DB_NAME = "crawl4ai"
DB_HOST = "localhost"
DB_PORT = "5434"

# Build the database URL
DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Log the database URL (with password masked)
masked_url = DATABASE_URL.replace(DB_PASSWORD, "********")
logger.info(f"Connecting to database: {masked_url}")

# Set the environment variable explicitly
os.environ["DATABASE_URL"] = DATABASE_URL
logger.info("Set DATABASE_URL environment variable")

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

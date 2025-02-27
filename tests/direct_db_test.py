"""
Direct database connection test.
"""

import logging

import psycopg2

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

# Connection string
CONNECTION_STRING = (
    f"dbname='{DB_NAME}' user='{DB_USER}' password='{DB_PASSWORD}'"
    f" host='{DB_HOST}' port='{DB_PORT}'"
)

logger.info(
    f"Attempting to connect with: dbname='{DB_NAME}' user='{DB_USER}'"
    f" password='********' host='{DB_HOST}' port='{DB_PORT}'"
)

try:
    # Connect to the database
    logger.info("Connecting to PostgreSQL database...")
    conn = psycopg2.connect(CONNECTION_STRING)

    # Create a cursor
    cursor = conn.cursor()

    # Execute a simple query
    logger.info("Executing test query...")
    cursor.execute("SELECT 1")

    # Fetch the result
    result = cursor.fetchone()
    logger.info(f"Query result: {result}")

    # Close the cursor and connection
    cursor.close()
    conn.close()
    logger.info("Connection closed successfully")

except Exception as e:
    logger.error(f"Error: {str(e)}")
    import traceback

    logger.error(f"Exception traceback: {traceback.format_exc()}")

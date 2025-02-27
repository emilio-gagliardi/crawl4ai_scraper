import asyncio
import logging
import sys

import debugpy
import uvicorn
from sqlalchemy import text
from sqlmodel import Session, select

from crawl4ai_scraper.backend.database import DATABASE_URL, engine, init_db

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Use ProactorEventLoop on Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

if __name__ == "__main__":
    # Skip debugpy for now as it's causing issues
    # debugpy.listen(("localhost", 5679))
    # print("Waiting for debugger attach...")

    # Print the actual database URL being used (with password masked)
    masked_url = DATABASE_URL
    if ":" in masked_url and "@" in masked_url:
        # Extract the password part and replace it with asterisks
        parts = masked_url.split("@")
        credentials = parts[0].split(":")
        if len(credentials) > 2:
            # Handle the case where there might be colons in the password
            password_part = ":".join(credentials[2:])
            masked_url = masked_url.replace(password_part, "********")
        else:
            # Simple case: username:password@host
            masked_url = masked_url.replace(credentials[1], "********")

    logger.info(f"Using database URL: {masked_url}")

    # Test database connection directly
    try:
        logger.info("Testing direct database connection...")
        with Session(engine) as session:
            # Try a simple query
            result = session.exec(text("SELECT 1")).first()
            logger.info(f"Database connection test successful: {result}")
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        import traceback

        logger.error(f"Exception traceback: {traceback.format_exc()}")
        # Continue anyway to see if the app can start

    # Initialize database
    try:
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        import traceback

        logger.error(f"Exception traceback: {traceback.format_exc()}")
        # Continue anyway to see if the app can start

    # Run the FastAPI app with uvicorn
    uvicorn.run(
        "crawl4ai_scraper.main:app",
        host="localhost",
        port=8002,
        log_level="debug",
        reload=True,
    )

import logging
import os

from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine

# Configure logging
logger = logging.getLogger(__name__)

# Print all environment variables for debugging
# logger.info("Environment variables:")
# for key, value in os.environ.items():
#     if key.startswith("POSTGRES_"):
#         if "PASSWORD" in key:
#             logger.info(f"{key}=********")
#         else:
#             logger.info(f"{key}={value}")

# Cache environment variables
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv(
    "POSTGRES_PORT", "5435"
)  # Default to 5435 for dev environment

# Print the individual connection parameters (with password masked)
# logger.info(f"DB_USER: {DB_USER}")
# logger.info(f"DB_PASSWORD: {'*' * 8 if DB_PASSWORD else None}")
# logger.info(f"DB_NAME: {DB_NAME}")
# logger.info(f"DB_HOST: {DB_HOST}")
# logger.info(f"DB_PORT: {DB_PORT}")

# Build the database URL from environment variables
# Use DATABASE_URL if explicitly provided, otherwise build from components
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)

# Log the database URL (with password masked)
masked_url = (
    DATABASE_URL.replace(DB_PASSWORD, "********")
    if DB_PASSWORD in DATABASE_URL
    else DATABASE_URL
)
logger.info(f"Connecting to database: {masked_url}")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=False)


def create_db_and_tables():
    """Create all the tables defined in the models."""
    logger.info("Creating database tables")
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created")


def get_db():
    """
    Create a new database session for each request.
    This is used as a FastAPI dependency.
    """
    logger.info("get_db called - creating new database session")
    logger.info(f"Using DATABASE_URL: {masked_url}")

    try:
        # Create a new session
        session = Session(engine)

        # Test the connection
        try:
            # Execute a simple query to test the connection
            session.exec(text("SELECT 1"))
        except Exception:
            # Close the session if the test fails
            session.close()
            raise

        # Yield the session to the endpoint
        yield session

        # Close the session after the endpoint is done
        logger.info("Closing database session")
        session.close()
    except Exception as e:
        logger.error(f"Database session error: {e}")
        raise

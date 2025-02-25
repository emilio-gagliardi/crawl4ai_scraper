import os

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

# Load environment variables
load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://crawl4ai:crawl4ai@db:5432/crawl4ai"
)

# Create engine
engine = create_engine(DATABASE_URL, echo=True, pool_size=5, max_overflow=10)


def init_db():
    """Initialize the database and create all tables."""
    SQLModel.metadata.create_all(engine)


def create_db_and_tables():
    """Create database tables."""
    init_db()


def get_db():
    """Get a database session.

    This function is used as a dependency in FastAPI endpoints
    to get a database session that is automatically closed
    after the request is complete.

    Yields:
        Session: SQLModel database session
    """
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()

import debugpy
import uvicorn

from crawl4ai_scraper.backend.database import init_db
from crawl4ai_scraper.backend.main import app

if __name__ == "__main__":
    # Enable debugging
    debugpy.listen(("localhost", 5678))
    print("⚡ Debugger is listening on port 5678")
    print("   You can now attach your debugger")

    # Initialize the database
    init_db()

    # Run the FastAPI app with uvicorn
    uvicorn.run(app, host="localhost", port=8002, log_level="debug")

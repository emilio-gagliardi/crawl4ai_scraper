# LLM Guidance File

## Project Rules and Preferences

- **Coding Style:** Follow PEP 8 for Python code.
- **Error Handling:** Implement robust error handling and logging.
- **Dependencies:** Manage dependencies using `requirements.txt` for the backend and `package.json` (if applicable) for the frontend.
- **Configuration:** Use `config.yaml` for application parameters and `.env` for sensitive information like API keys.
- **Docker:** Containerize the application using Docker and Docker Compose.
- **Frontend:** Use Streamlit for the frontend.
- **Asynchronous Operations:** Utilize asynchronous programming where appropriate to improve performance.

## Testing and Development Plan

### Phase 1: Local Environment Setup

1. **Virtual Environment Setup**
   ```bash
   # Using existing conda environment
   conda activate crawl4ai_scraper_venv
   pip install --upgrade pip
   ```

2. **Dependencies Installation**
   ```bash
   cd crawl4ai_scraper
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   ```bash
   # Generate encryption key
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   
   # Update .env file with the generated key and database settings
   # DATABASE_URL=postgresql://user:password@localhost:5433/crawl4ai  # Using port 5433 instead of 5432
   # ENCRYPTION_KEY=<generated_key>
   # OUTPUT_DIR=./data/scrapes
   ```

4. **PostgreSQL Setup**
   ```bash
   # Install PostgreSQL if not already installed
   # Create database and user (using port 5433)
   psql -U postgres -p 5433
   CREATE DATABASE crawl4ai;
   CREATE USER crawl4ai WITH PASSWORD 'crawl4ai';
   GRANT ALL PRIVILEGES ON DATABASE crawl4ai TO crawl4ai;
   ```

### Phase 2: Backend Testing

1. **Start Backend Server**
   ```bash
   cd crawl4ai_scraper
   uvicorn backend.main:app --reload --port 8002  # Changed from 8000
   ```

2. **API Testing Commands**
   ```bash
   # Test backend health
   curl http://localhost:8002/
   
   # Test providers endpoint
   curl http://localhost:8002/api/credentials/providers
   
   # Test scraping endpoint
   curl -X POST http://localhost:8002/api/scrape \
     -H "Content-Type: application/json" \
     -d '{"urls": ["https://example.com"], "config": {...}}'
   ```

### Phase 3: Frontend Testing

1. **Start Frontend Server**
   ```bash
   cd crawl4ai_scraper
   streamlit run frontend/app.py --server.port 8502  # Changed from 8501
   ```

2. **Access Points**
   - Frontend UI: http://localhost:8502
   - Backend API docs: http://localhost:8002/docs

## Best Practices

### Security
1. **API Key Management**
   - Never commit API keys or sensitive data
   - Use environment variables for secrets
   - Implement key rotation mechanism
   - Encrypt sensitive data at rest

2. **Database Security**
   - Use strong passwords
   - Limit database user privileges
   - Regular backup procedures
   - Implement connection pooling

3. **Input Validation**
   - Validate all user inputs
   - Sanitize URLs before scraping
   - Implement rate limiting
   - Add request size limits

### Performance
1. **Resource Management**
   - Implement connection pooling
   - Use async operations for I/O
   - Implement proper cleanup
   - Monitor memory usage

2. **Caching Strategy**
   - Cache provider listings
   - Implement result caching
   - Use ETags for API responses
   - Regular cache invalidation

3. **Error Handling**
   - Implement comprehensive logging
   - Use structured error responses
   - Add request tracing
   - Implement circuit breakers

### Development Workflow
1. **Code Quality**
   - Run pre-commit hooks
   - Regular dependency updates
   - Code review processes
   - Documentation updates

2. **Testing Strategy**
   - Manual endpoint testing
   - UI functionality testing
   - Performance monitoring
   - Error scenario testing

## API Design Principles

### FastAPI Best Practices

1. **Data Validation and Schemas**
   - Use Pydantic models for ALL request and response data
   - Define schemas in `schemas.py` with proper Field definitions and examples
   - Never return raw dictionaries or lists from API endpoints
   - Include comprehensive docstrings and examples in schema definitions

2. **Schema Organization**
   ```python
   # Request Models (Input Validation)
   class UserCreate(BaseModel):
       username: str = Field(..., description="User's username", example="john_doe")
       email: EmailStr = Field(..., description="User's email", example="john@example.com")

   # Response Models (Output Validation)
   class UserResponse(BaseModel):
       id: int = Field(..., description="User's unique identifier", example=1)
       username: str = Field(..., description="User's username", example="john_doe")
       created_at: datetime = Field(..., description="Account creation timestamp")
   ```

3. **Route Structure**
   - Group related endpoints under a common router
   - Use proper HTTP methods (GET, POST, PUT, DELETE)
   - Include response_model in route decorators
   - Document all parameters and responses

   ```python
   @router.post("/users/", response_model=UserResponse)
   async def create_user(user: UserCreate) -> UserResponse:
       """Create a new user.
       
       Args:
           user: User creation data
           
       Returns:
           Created user information
           
       Raises:
           HTTPException: If user creation fails
       """
   ```

4. **Model Separation**
   - `models.py`: SQLModel database models
   - `schemas.py`: Pydantic API schemas
   - Keep database models and API schemas separate for flexibility

### Database Layer

1. **SQLModel Usage**
   - Use SQLModel for database operations
   - Prefer select() over raw SQL queries
   - Use proper type hints with Session

2. **Service Layer**
   - Implement business logic in service classes
   - Handle database operations through services
   - Keep routes focused on request/response handling

## API Design Standards

### Response Structure

1. **Standardized Response Format**
   All API responses follow a consistent structure:
   ```json
   {
     "status": "success | error | pending",
     "message": "Human-readable description",
     "code": 200,
     "data": { ... }
   }
   ```

2. **Status Codes**
   - Use application-specific status codes for fine-grained control
   - Success codes (2xx): 200 (Success), 201 (Created), 202 (Accepted)
   - Error codes (4xx): 400 (Invalid Request), 401 (Unauthorized), 404 (Not Found)
   - Processing codes (1xx): 100 (Pending), 102 (Processing)

3. **Type Safety**
   - Use generic type parameters for response payloads
   - Define specific response types for each endpoint
   - Example:
   ```python
   CredentialResponse = APIResponse[CredentialData]
   ProviderListResponse = APIResponse[List[ProviderInfo]]
   ```

4. **Error Handling**
   - Always return a valid response object, even for errors
   - Include helpful error messages in the 'message' field
   - Set appropriate status codes
   - Example error response:
   ```json
   {
     "status": "error",
     "message": "Failed to create credentials: Invalid API key",
     "code": 400,
     "data": null
   }
   ```

5. **Response Models**
   - Define clear Pydantic models for all response data
   - Include comprehensive field descriptions and examples
   - Use proper type hints and validation
   - Example:
   ```python
   class CredentialData(BaseModel):
       provider: str = Field(..., description="Provider name")
       model: str = Field(..., description="Model name")
       created_at: datetime
       is_active: bool
   ```

### Implementation Guide

1. **Schema Organization**
   - Keep all schemas in `schemas.py`
   - Group related schemas together
   - Use clear naming conventions (e.g., `*Request`, `*Response`, `*Data`)

2. **Route Implementation**
   - Always specify `response_model` in route decorators
   - Return properly structured response objects
   - Handle errors gracefully with appropriate status codes

3. **Documentation**
   - Include comprehensive docstrings
   - Document all parameters and return types
   - Provide examples in schema definitions

4. **Testing**
   - Verify response structure in tests
   - Test both success and error cases
   - Validate response data against schemas

## Environment Selection

We've implemented multiple ways to select which environment the application runs in:

### 1. Using the `environment.py` File

The simplest way to set the environment is to edit the `environment.py` file in the project root:

```python
# Set the environment here
# Options: 'dev' or 'prod'
ENVIRONMENT = 'dev'  # Change to 'prod' for production
```

### 2. Using Command-Line Arguments

You can specify the environment when running the application:

```bash
# Run in development mode
python run.py --env dev

# Run in production mode
python run.py --env prod
```

### 3. Using Environment Variables

You can set the `ENV` environment variable before running the application:

```bash
# On Windows PowerShell
$env:ENV="prod"
python run.py

# On Windows Command Prompt
set ENV=prod
python run.py
```

### Priority Order

The environment is determined in the following order of precedence:

1. Command-line argument (`--env`)
2. Environment variable (`ENV`)
3. `environment.py` file
4. Default to `dev`

This flexible approach allows you to easily switch between environments without modifying code.

## Robust Path Management for Environment Files

To address the fragility of using relative paths with multiple `parent.parent.parent` calls, we've implemented a more robust solution for finding the project root and loading environment files:

### 1. Created a Paths Utility Module

We created a new utility module `paths.py` that provides functions for reliably finding the project root and environment files:

```python
def get_project_root() -> Path:
    """
    Get the absolute path to the project root directory.
    This is more robust than using relative paths with parent.parent.parent...
    """
    # Start from the current file
    current_path = Path(__file__).resolve()
    
    # Navigate up until we find the project root (where we expect to find .env or dev.env)
    for parent in [current_path, *current_path.parents]:
        # Check for markers that indicate we're at the project root
        if (parent / "dev.env").exists() or (parent / ".env").exists() or (parent / "run.py").exists():
            return parent
    
    # If we couldn't find the project root, use a reasonable default
    return Path(__file__).resolve().parent.parent.parent.parent

def get_env_file_path(env_name: str = None) -> Path:
    """
    Get the path to the environment file based on the current environment.
    """
    # Determine environment
    env = env_name or os.getenv("ENV", "dev")
    env_file = "dev.env" if env == "dev" else ".env"
    
    # Return the absolute path to the environment file
    return get_project_root() / env_file
```

### 2. Updated All Modules to Use the Paths Utility

Instead of hard-coding relative paths, all modules now use the utility functions:

```python
from .utils.paths import get_env_file_path

# Determine environment
ENV = os.getenv("ENV", "dev")

# Load environment variables
env_path = get_env_file_path(ENV)
load_dotenv(env_path)
logger.info(f"Loaded environment from: {env_path}")
```

### 3. Benefits of This Approach

1. **Resilience to Refactoring**: The code will continue to work even if files are moved or the project structure changes
2. **Self-Documenting**: The code clearly shows its intent rather than relying on obscure path manipulations
3. **Centralized Logic**: Path-finding logic is in one place, making it easier to update if needed
4. **Error Handling**: The utility includes fallback mechanisms if the project root can't be found

### 4. Importing in the Run Script

For the run.py script (which is outside the package), we added the project root to the Python path:

```python
# Add the project root to the Python path to allow importing from the package
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the paths utility
from crawl4ai_scraper.backend.utils.paths import get_env_file_path
```

This approach ensures consistent environment loading across all parts of the application without relying on fragile path constructions.

## Docker Configuration and Best Practices

### Container Structure
- **Backend Container**: Uses Python 3.11 slim image with necessary system dependencies for PostgreSQL.
- **Frontend Container**: Uses Python 3.11 slim image for Streamlit application.
- **Database Container**: Uses PostgreSQL 15 with persistent volume storage.

### Key Docker Decisions
1. **Database Connection**:
   - Always use `db:5432` as the database host:port in Docker environment, not localhost.
   - The database service name in docker-compose.yml (`db`) is used as the hostname.

2. **Environment Variables**:
   - Sensitive information like `ENCRYPTION_KEY` should be passed through environment variables.
   - Default values are provided in docker-compose.yml for development, but should be overridden in production.

3. **Volume Mounts**:
   - Data persistence is handled through Docker volumes:
     - `postgres_data`: For database persistence
     - `shared_storage`: For sharing data between containers
     - `./data:/app/data`: Host-mounted directory for storing scrape results

4. **Network Configuration**:
   - All services are on the same Docker network (`crawl4ai-network`).
   - External ports are mapped to avoid conflicts (e.g., 5434:5432 for PostgreSQL).

5. **Dependency Management**:
   - When updating dependencies in requirements.txt, rebuild containers with `docker-compose up -d --build`.
   - Pydantic v2 compatibility must be maintained across all schema definitions.

### Code Compatibility with Docker
1. **File Paths**:
   - Use relative paths from the application root (`/app` in the container).
   - For persistent storage, use the mounted volumes (`/app/data` or `/app/shared`).

2. **Service Discovery**:
   - Use service names from docker-compose.yml for inter-service communication.
   - Backend API is accessible at `http://backend:8002` from other containers.

3. **Database Schema Updates**:
   - Database tables should be created on application startup using `create_db_and_tables()`.
   - Table names in models must match exactly with the database schema (e.g., `scrape_metadata` not `scrapemetadata`).

## Required Command Whitelist

To whitelist these commands for the AI assistant, you need to approve the following command patterns:

### System Commands
```bash
conda activate crawl4ai_scraper_venv
pip install -r requirements.txt
python -c "<command>"
psql -U postgres -p 5433
uvicorn backend.main:app --reload --port 8002
streamlit run frontend/app.py --server.port 8502
curl http://localhost:8002/
git add .
git commit -m "message"
git status
ls
cd <directory>
mkdir <directory>
mv <source> <destination>
rm <file>
cat <file>
```

### Database Commands (Port 5433)
```sql
CREATE DATABASE crawl4ai;
CREATE USER crawl4ai WITH PASSWORD 'crawl4ai';
GRANT ALL PRIVILEGES ON DATABASE crawl4ai TO crawl4ai;
```

### Environment Management
```bash
conda activate crawl4ai_scraper_venv
conda deactivate
```

Note: To whitelist these commands, you'll need to explicitly approve them when the AI assistant attempts to use them. The AI will request permission before executing any command that could modify your system.

## Testing Workflow

1. **Initial Setup Verification**
   - Check virtual environment activation
   - Verify dependency installation
   - Confirm database connection
   - Test environment variables

2. **Backend Verification**
   - Start backend server
   - Check API documentation
   - Test health endpoint
   - Verify database migrations

3. **Frontend Verification**
   - Start frontend server
   - Check UI rendering
   - Test API connectivity
   - Verify form submissions

4. **Integration Testing**
   - Test credential management
   - Test scraping configuration
   - Verify data extraction
   - Check error handling

5. **Error Recovery**
   - Database connection issues
   - API timeout handling
   - Invalid credential handling
   - Resource cleanup

## Common Issues and Solutions

1. **Database Connection**
   - Check PostgreSQL service status
   - Verify connection string
   - Check user permissions
   - Test network connectivity

2. **API Errors**
   - Check server logs
   - Verify request format
   - Check API key validity
   - Test endpoint availability

3. **Frontend Issues**
   - Check browser console
   - Verify API endpoint URLs
   - Check form validation
   - Test responsive design

4. **Scraping Issues**
   - Check URL accessibility
   - Verify extraction strategy
   - Check output directory permissions
   - Monitor resource usage

## Database Connection and Encryption Key Issues

### Problem Statement

The application is experiencing database connection issues when accessing the `/api/scrape` endpoint. The issue stems from:

1. **Inconsistent Database Connection Strings**:
   - At startup, the application connects to: `postgresql://crawl4ai:your_secure_password_here@localhost:5434/crawl4ai`
   - When the `/api/scrape` endpoint is accessed, it attempts to connect to: `localhost:5432` with user `user`

2. **Encryption Key Management**:
   - The current implementation stores the encryption key in the `.env` file
   - The encryption module appends to `.env` when generating a new key, potentially causing conflicts
   - Multiple parts of the application read the `.env` file, leading to inconsistent environment variables

### Proposed Solution

#### 1. Encryption Key Storage
Move encryption key storage from `.env` to a dedicated file:
- Store the key in `data/encryption_key.key`
- Cache the key in memory to prevent repeated file operations
- Validate the key before use and regenerate if invalid

#### 2. Development Environment Separation
Create a dedicated development environment:
- Use `dev.env` for local development configuration
- Create `docker-compose.dev.yml` for development database only
- Update `run.py` to explicitly use the development environment

#### 3. Database Connection Caching
Prevent environment variable reloading:
- Cache database parameters in `database.py` to prevent re-reading environment
- Use a single engine instance throughout the application
- Add explicit debug logging for connection strings

#### 4. Consistent Fernet Instance
Ensure all parts of the application use the same encryption:
- Export the Fernet instance from the encryption module
- Import and use this instance in the credentials service

### Implementation Steps

1. **Update encryption.py**: Store key in a file instead of `.env`
2. **Create dev.env**: Separate development environment configuration
3. **Update run.py**: Use development environment file
4. **Create docker-compose.dev.yml**: Development database configuration
5. **Update database.py**: Cache connection parameters
6. **Update credentials.py**: Use shared Fernet instance

### Development Workflow

1. Start only the database container for development:
   ```
   docker-compose -f docker-compose.dev.yml up db
   ```

2. Run the FastAPI app locally:
   ```
   python run.py
   ```

2. **For Production**:
   ```bash
   # Set environment to production
   export ENV=prod
   
   # Start all services
   docker-compose up -d
   ```

This approach provides flexibility while maintaining consistency across environments.

## Database Connection Issues: Problem and Resolution

### Problem Description

The application was experiencing database connection issues due to conflicts in environment variable settings across multiple locations. Specifically:

1. **Multiple .env Files**: The application had .env files in both the project root and the application root directories, causing conflicts in environment variable values.

2. **Inconsistent Port Configuration**: The Docker container was exposing PostgreSQL on port 5435, but the application was trying to connect to port 5434.

3. **Environment Variable Loading**: Multiple modules were loading environment variables independently without specifying which .env file to use, leading to unpredictable behavior.

4. **Connection String Construction**: The DATABASE_URL was being constructed using environment variables that might have been overridden or set incorrectly.

### Resolution Steps

1. **Removed Nested .env File**: Deleted the .env file in the application root directory (`crawl4ai_scraper/crawl4ai_scraper/.env`) that was setting incorrect database connection parameters.

2. **Standardized Environment File Loading**: Updated all `load_dotenv()` calls to explicitly load from the development environment file (`dev.env`) using absolute paths:
   ```python
   load_dotenv(Path(__file__).parent.parent.parent / "dev.env")
   ```

3. **Hardcoded Critical Connection Parameters**: Ensured the database port was correctly set by hardcoding it in the database.py file:
   ```python
   DB_PORT = "5435"  # Hardcoded to match Docker container
   ```

4. **Forced DATABASE_URL Construction**: Added code to force the DATABASE_URL to use the correct parameters regardless of environment variables:
   ```python
   DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
   ```

5. **Updated Port in Development Environment**: Ensured the port in dev.env matched the port exposed by the Docker container (5435).

### Prescriptive Rules for Future FastAPI-Docker Applications

To avoid similar issues in future FastAPI applications with Docker, follow these rules:

1. **Environment File Structure**:
   - Keep all .env files in the project root directory, not in subdirectories
   - Use separate files for different environments (dev.env, prod.env, etc.)
   - Never commit .env files to version control (add to .gitignore)

2. **Docker Configuration**:
   - Ensure Docker Compose port mappings match the ports specified in environment files
   - Use consistent naming conventions for services and environment variables
   - Document port mappings clearly in README.md

3. **Environment Variable Loading**:
   - Always specify the path to the .env file when calling load_dotenv()
   - Load environment variables once at application startup, not in multiple modules
   - Use a centralized configuration module that other modules can import

4. **Connection String Management**:
   - Construct database connection strings in one place only
   - Log masked connection strings (hiding passwords) for debugging
   - Consider using a configuration class to manage connection parameters

5. **Explicit Over Implicit**:
   - Explicitly set critical configuration parameters rather than relying on defaults
   - Use environment variable validation to catch configuration errors early
   - Add debug logging for connection parameters

### Exact Steps for Setting Up a New FastAPI-Docker Application

1. **Project Structure Setup**:
   ```
   project_root/
   ├── app/
   │   ├── main.py
   │   ├── database.py
   │   └── ...
   ├── docker-compose.yml
   ├── docker-compose.dev.yml
   ├── .env.example
   ├── dev.env
   └── README.md
   ```

2. **Environment Configuration**:
   - Create a `dev.env` file with development settings
   - Create a `.env.example` file with placeholder values as documentation
   - Add all .env files to .gitignore except .env.example

3. **Database Connection Setup**:
   - In `database.py`, load environment variables explicitly:
     ```python
     from pathlib import Path
     from dotenv import load_dotenv
     
     # Load environment variables from dev.env
     load_dotenv(Path(__file__).parent.parent.parent / "dev.env")
     
     # Construct DATABASE_URL explicitly
     DB_USER = os.getenv("POSTGRES_USER")
     DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
     DB_NAME = os.getenv("POSTGRES_DB")
     DB_HOST = os.getenv("POSTGRES_HOST")
     DB_PORT = os.getenv("POSTGRES_PORT")
     
     DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
     ```

4. **Docker Configuration**:
   - In `docker-compose.dev.yml`, ensure port mappings match environment variables:
     ```yaml
     services:
       db:
         image: postgres:15
         environment:
           - POSTGRES_USER=${POSTGRES_USER}
           - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
           - POSTGRES_DB=${POSTGRES_DB}
         ports:
           - "${POSTGRES_PORT}:5432"
     ```

5. **Application Startup**:
   - In `main.py`, ensure environment variables are loaded before any database operations:
     ```python
     import os
     from pathlib import Path
     from dotenv import load_dotenv
     
     # Load environment variables at startup
     load_dotenv(Path(__file__).parent.parent.parent / "dev.env")
     
     # Import database after loading environment variables
     from app.database import get_db, create_db_and_tables
     ```

6. **Testing Connection**:
   - Add a health check endpoint to verify database connection:
     ```python
     @app.get("/health")
     def health_check(db: Session = Depends(get_db)):
         try:
             # Execute a simple query
             db.execute(text("SELECT 1"))
             return {"status": "healthy", "database": "connected"}
         except Exception as e:
             return {"status": "unhealthy", "database": str(e)}
     ```

By following these guidelines, you'll avoid the common pitfalls of environment configuration and database connection issues in FastAPI applications with Docker.

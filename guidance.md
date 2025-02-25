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

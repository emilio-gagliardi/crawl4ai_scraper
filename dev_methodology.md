# Development Methodology for Dockerized Applications

## Current State Analysis

The project is set up with:
- A Docker Compose configuration with three services: PostgreSQL database, FastAPI backend, and Streamlit frontend
- Local development scripts (`run.py` and `debug_server.py`) for running the application outside Docker
- Git version control already initialized

## Recommended Development Workflow

### 1. Development Environment Options

#### Option A: Development Outside Docker (Recommended for Active Development)

This approach allows for faster iteration during development:

1. **Run the database in Docker, but backend and frontend locally:**
   - Use `docker-compose up db` to start only the PostgreSQL container
   - Run the backend with `python run.py` or `python debug_server.py` for debugging
   - Run the frontend with `streamlit run crawl4ai_scraper/frontend/app.py`
   - Configure environment variables to connect to the Docker database (e.g., `DATABASE_URL=postgresql://crawl4ai:crawl4ai@localhost:5434/crawl4ai`)

2. **Benefits:**
   - Immediate code reloading without rebuilding containers
   - Easy debugging with IDE integration
   - Fast iteration cycles

#### Option B: Development Inside Docker with Volume Mounts

For when you need to test the full Docker environment:

1. **Modify docker-compose.yml to add code volume mounts:**

```yaml
backend:
  # ... existing config ...
  volumes:
    - ./crawl4ai_scraper:/app/crawl4ai_scraper  # Mount code directory
    - ./data:/app/data
    - shared_storage:/app/shared

frontend:
  # ... existing config ...
  volumes:
    - ./crawl4ai_scraper:/app/crawl4ai_scraper  # Mount code directory
    - ./data:/app/data
    - shared_storage:/app/shared
```

2. **Enable hot-reloading in containers:**
   - For backend, ensure the uvicorn command has `--reload` flag
   - For frontend, Streamlit has hot-reloading by default

3. **Benefits:**
   - Tests the full Docker environment
   - Changes to code are reflected without rebuilding

### Understanding Volume Mounts

Volume mounts create a bidirectional link between a directory on your host machine (your local development environment) and a directory inside the Docker container. This means:

1. **Real-time code sharing:** When you edit a file locally, the changes are immediately visible inside the container
2. **No rebuild required:** You don't need to rebuild the Docker image to see code changes
3. **Persistence:** Data written to these directories persists even if the container is destroyed

Example of how this works:

- You edit `crawl4ai_scraper/backend/crud.py` in your IDE
- The file is automatically updated inside the container at `/app/crawl4ai_scraper/backend/crud.py`
- If your application has hot-reloading enabled, it will detect the change and restart
- You see the changes immediately without having to rebuild or restart the container manually

This creates a seamless development experience where you can work in your familiar local environment while running the application in a containerized environment that matches production.

### 2. Git Branching Strategy

A simplified Git Flow approach is recommended:

#### Main Branches

- **`main` (or `master`)**: Production-ready code
  - Always deployable
  - Contains released versions of the code
  - Protected from direct commits

- **`develop`**: Integration branch for features
  - Contains the latest delivered development changes for the next release
  - Where feature branches are merged into
  - May be unstable at times

#### Supporting Branches

- **`feature/*`**: New features (branch from `develop`)
  - Used to develop new features
  - Merged back into `develop` when complete
  - Naming convention: `feature/descriptive-feature-name`

- **`bugfix/*`**: Bug fixes (branch from `develop`)
  - Used to fix bugs in the development code
  - Merged back into `develop` when complete

- **`release/*`**: Release preparation (branch from `develop`)
  - Used to prepare for a new production release
  - Minor bug fixes and preparation for release
  - Merged into both `main` and `develop` when ready

- **`hotfix/*`**: Urgent fixes for production (branch from `main`)
  - Used to quickly fix critical bugs in production
  - Merged into both `main` and `develop`

#### Detailed Workflow with Commands

1. **Starting a new feature**

   Begin by ensuring you're on the develop branch and it's up to date:

   ```bash
   # Switch to develop branch
   git checkout develop
   
   # Pull latest changes
   git pull origin develop
   
   # Create a new feature branch
   git checkout -b feature/implement_crud_postgresql
   ```

2. **Working on your feature**

   Make changes, commit frequently with descriptive messages:

   ```bash
   # Make changes to files
   # ...
   
   # Add changed files
   git add crawl4ai_scraper/backend/crud.py
   
   # Commit changes with descriptive message
   git commit -m "Implement basic CRUD operations for PostgreSQL"
   
   # Push your branch to remote (first time)
   git push -u origin feature/implement_crud_postgresql
   
   # For subsequent pushes
   git push
   ```

3. **Keeping your feature branch up to date with develop**

   Regularly incorporate changes from develop to avoid merge conflicts later:

   ```bash
   # Switch to develop branch
   git checkout develop
   
   # Pull latest changes
   git pull origin develop
   
   # Switch back to feature branch
   git checkout feature/implement_crud_postgresql
   
   # Merge develop into your feature branch
   git merge develop
   
   # Resolve any conflicts if they occur
   # ...
   
   # Push updated feature branch
   git push
   ```

4. **Completing a feature**

   When your feature is complete and tested:

   ```bash
   # Ensure your feature branch is up to date with develop
   git checkout develop
   git pull origin develop
   git checkout feature/implement_crud_postgresql
   git merge develop
   
   # Resolve any conflicts
   # ...
   
   # Push final changes
   git push
   ```

5. **Merging a feature into develop**

   There are two approaches:

   **Option A: Direct merge (for smaller features)**
   ```bash
   # Switch to develop branch
   git checkout develop
   
   # Merge feature branch into develop
   git merge --no-ff feature/implement_crud_postgresql
   
   # Push changes to remote develop
   git push origin develop
   
   # Delete feature branch (optional)
   git branch -d feature/implement_crud_postgresql
   git push origin --delete feature/implement_crud_postgresql
   ```

   **Option B: Pull Request (for larger features or team workflows)**
   - Create a Pull Request in GitHub/GitLab/etc.
   - Have team members review the code
   - Merge through the platform's interface

### Pull Requests vs. Direct Merges

#### When to use Pull Requests:

1. **Team environments**: When multiple developers need to review code
2. **Complex features**: When changes are substantial and need careful review
3. **Quality control**: When you want to enforce code review policies
4. **Documentation**: PRs provide a record of changes and discussions

#### When to use Direct Merges:

1. **Solo development**: When you're the only developer
2. **Simple changes**: For minor bug fixes or small enhancements
3. **Rapid iteration**: When you need to move quickly without overhead

#### Squash Merging vs. Regular Merging

**Squash Merging**: Combines all commits from a feature branch into a single commit when merging

**When to use Squash Merging:**
1. **Clean history**: When you want a cleaner, more concise main branch history
2. **Messy feature branches**: When feature branches contain many small, incremental commits
3. **Logical units**: When you want each feature to appear as a single, atomic change

**When to use Regular Merging:**
1. **Detailed history**: When you want to preserve the full development history
2. **Well-structured commits**: When feature branch commits are already well-organized
3. **Traceability**: When you need to trace the evolution of changes within a feature

## Implementation Steps for the Project

### Step 1: Set Up Local Development Environment

1. Create a `.env.local` file for local development:

```
DATABASE_URL=postgresql://crawl4ai:crawl4ai@localhost:5434/crawl4ai
API_URL=http://localhost:8002
ENCRYPTION_KEY=your_encryption_key
```

2. Create a script to start the database only:

```bash
# start_db.ps1 (PowerShell)
docker-compose up -d db
```

3. Create a script to run the application locally:

```bash
# run_local.ps1 (PowerShell)
# Load environment variables from .env.local
Get-Content .env.local | ForEach-Object {
    if ($_ -match "(.+)=(.+)") {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2])
    }
}

# Start the backend in one terminal
Start-Process powershell -ArgumentList "-Command python run.py"

# Start the frontend in another terminal
Start-Process powershell -ArgumentList "-Command streamlit run crawl4ai_scraper/frontend/app.py"
```

### Step 2: Set Up Git Branches

1. Ensure your current work is committed to `master`:

```bash
git add .
git commit -m "Complete Docker setup and base functionality"
```

2. Create a develop branch:

```bash
git checkout -b develop
git push -u origin develop
```

3. Create your first feature branch:

```bash
git checkout -b feature/implement_crud_postgresql
git push -u origin feature/implement_crud_postgresql
```

### Step 3: Update Docker Compose for Development

Modify your docker-compose.yml to support development with code hot-reloading:

```yaml
backend:
  # ... existing config ...
  command: ["uvicorn", "crawl4ai_scraper.main:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]
  volumes:
    - ./crawl4ai_scraper:/app/crawl4ai_scraper
    - ./data:/app/data
    - shared_storage:/app/shared

frontend:
  # ... existing config ...
  volumes:
    - ./crawl4ai_scraper:/app/crawl4ai_scraper
    - ./data:/app/data
    - shared_storage:/app/shared
```

### Step 4: Example Feature Implementation - CRUD Operations

For implementing the `feature/implement_crud_postgresql` branch:

1. Create the branch:
```bash
git checkout develop
git pull origin develop
git checkout -b feature/implement_crud_postgresql
```

2. Implement and test CRUD operations:
   - Update database models
   - Implement CRUD functions
   - Write tests
   - Test locally

3. Commit changes:
```bash
git add crawl4ai_scraper/backend/crud.py
git add crawl4ai_scraper/backend/models.py
git add tests/test_crud.py
git commit -m "Implement CRUD operations for PostgreSQL"
git push -u origin feature/implement_crud_postgresql
```

4. Keep in sync with develop:
```bash
git checkout develop
git pull origin develop
git checkout feature/implement_crud_postgresql
git merge develop
# Resolve any conflicts
git push
```

5. When complete, merge back to develop:
```bash
git checkout develop
git merge --no-ff feature/implement_crud_postgresql
git push origin develop
```

6. Clean up:
```bash
git branch -d feature/implement_crud_postgresql
git push origin --delete feature/implement_crud_postgresql
```

## Conclusion

This methodology gives you flexibility to:
1. Develop quickly outside Docker when making frequent code changes
2. Test in Docker when needed without rebuilding containers
3. Use Git branches effectively for feature development
4. Maintain a clean separation between development and production environments

The key is to choose the right approach based on what you're working on:
- For rapid code iteration: Use local development with Docker database
- For testing Docker configuration: Use Docker with volume mounts
- For production deployment: Use standard Docker builds

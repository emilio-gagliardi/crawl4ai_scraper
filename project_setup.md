# Crawl4AI Scraper Application Documentation

## Overview
A dockerized web scraping solution that extracts content to markdown, captures screenshots, and applies LLM-powered extraction strategies.

## Technology Stack
### Core Components
- **Python 3.9+** (Backend services)
- **FastAPI** (REST API endpoints)
- **Playwright** (Headless browser automation)
- **Docker** (Containerization)
- **Docker Compose** (Orchestration)

### AI/ML Components
- **LLMExtractionStrategy** (Content analysis via language models)
- **Transformers** (NLP processing)

### Frontend
- **React** (UI components)
- **TypeScript** (Frontend implementation)
- **Material-UI** (UI components)

## Application Architecture
### Key Services
```mermaid
graph TD
    A[Client] --> B[NGINX]
    B --> C[Frontend]
    B --> D[Backend API]
    D --> E[Scraping Service]
    D --> F[LLM Processing]
    E --> G[Playwright Cluster]
    F --> H[Transformer Models]
```

### Data Flow
1. URL submission through React UI
2. API request routing via FastAPI
3. Playwright-based content acquisition
4. Markdown transformation & screenshot capture
5. LLM-powered content analysis
6. Result aggregation and response

## Coding Standards
### Backend (Python)
- PEP8 compliance enforced via pre-commit
- Type hints for all public methods
- Async-first implementation
- Pytest coverage > 80%

### Frontend (TypeScript)
- Strict null checks
- Functional components with hooks
- Atomic design pattern
- Cypress E2E testing

## Dockerization
### Service Architecture
```yaml
version: '3.8'
services:
  backend:
    build: ./docker/backend
    env_file: .env
  frontend:
    build: ./docker/frontend
    ports:
      - "3000:3000"
  playwright:
    image: mcr.microsoft.com/playwright
```

### Build Process
- Multi-stage Dockerfiles
- Slim Python base images
- Node.js 16.x for frontend
- Production-optimized builds

## Getting Started
### Prerequisites
```bash
docker-compose build
docker-compose up -d
```

### Environment Setup
```bash
# Windows
./setup.ps1

# Unix
chmod +x setup.sh
./setup.sh
```

## Assumptions & Constraints
1. Docker runtime available
2. NVIDIA GPU for LLM acceleration (optional)
3. Minimum 8GB RAM allocation
4. Network access to target domains
5. Valid API keys in .env file

## Contribution Guidelines
1. Feature branches from `develop`
2. Conventional commits
3. Draft PRs for WIP
4. Codeowner reviews required
5. Update integration tests

# Project Setup Guide

## Pre-commit Hook Configuration

### Overview
The project uses pre-commit hooks to ensure code quality and consistency. These hooks run automatically before each commit and check for:
- Code formatting (black)
- Import sorting (isort)
- Style and docstring compliance (flake8)

### Setup Process

1. **Configuration File**
   Create `.pre-commit-config.yaml` in the project root:
   ```yaml
   repos:
   -   repo: https://github.com/psf/black
       rev: 23.12.1
       hooks:
       -   id: black
           language_version: python3.11
           args: ['--line-length=79', '--skip-string-normalization', '--preview']

   -   repo: https://github.com/pycqa/flake8
       rev: 7.0.0
       hooks:
       -   id: flake8
           args: [
               '--ignore=D100,D400,D401,E501,F401',
               '--max-line-length=79'
           ]
           additional_dependencies: [flake8-docstrings]

   -   repo: https://github.com/pycqa/isort
       rev: 5.13.2
       hooks:
       -   id: isort
           args: ["--profile", "black", "--line-length=79"]
   ```

2. **Development Dependencies**
   Add the following to `requirements.txt`:
   ```
   # Development dependencies
   pre-commit>=3.6.0
   black==23.12.1
   flake8>=7.0.0
   flake8-docstrings>=1.7.0
   isort>=5.13.2
   ```

3. **Installation**
   ```bash
   # Install pre-commit and dependencies
   pip install -r requirements.txt
   
   # Install the git hooks
   pre-commit install
   ```

### Hook Details

1. **Black (Code Formatter)**
   - Line length: 79 characters
   - Skip string normalization (preserves single/double quotes)
   - Preview mode enabled for latest features
   - Automatically formats code to meet Python style guidelines

2. **Flake8 (Style Checker)**
   - Checks PEP 8 compliance
   - Validates docstrings (using flake8-docstrings)
   - Ignores specific rules:
     - D100: Missing module docstring
     - D400: First line should end with period
     - D401: First line should be in imperative mood
     - E501: Line too long
     - F401: Imported but unused

3. **isort (Import Sorter)**
   - Uses black-compatible settings
   - Line length: 79 characters
   - Groups and sorts imports according to PEP 8

### Usage

1. **Automatic Checks**
   - Hooks run automatically on `git commit`
   - Failed checks prevent commit until issues are fixed
   - Some issues are fixed automatically (formatting, import sorting)
   - Others require manual fixes (docstrings, style violations)

2. **Manual Running**
   ```bash
   # Check all files in the project
   pre-commit run --all-files
   
   # Check specific files
   pre-commit run --files path/to/file1.py path/to/file2.py
   ```

3. **Example Output**
   ```
   black....................................................................Passed
   flake8...................................................................Failed
   - hook id: flake8
   - exit code: 1
   crawl4ai_scraper/test_hooks.py:8:1: D403 First word of the first line should be properly capitalized
   isort....................................................................Passed
   ```

### Common Issues and Solutions

1. **Docstring Formatting**
   ```python
   # Incorrect
   def function():
       """this is incorrect.
       no blank line after summary.
       """
   
   # Correct
   def function():
       """This is correct.

       Has a capitalized first word and
       a blank line after the summary.
       """
   ```

2. **Import Organization**
   ```python
   # Incorrect
   import sys,os,json
   from typing import List,Dict
   
   # Correct (after isort)
   import json
   import os
   import sys
   from typing import Dict, List
   ```

3. **Code Formatting**
   ```python
   # Incorrect
   def bad_function(x,y,z='test'):return {'x':x,'y':y,'z':z}
   
   # Correct (after black)
   def good_function(
       x: int,
       y: int,
       z: str = 'test'
   ) -> Dict[str, Any]:
       return {'x': x, 'y': y, 'z': z}
   ```

### Bypassing Hooks
In rare cases where you need to bypass the hooks:
```bash
# Skip all pre-commit hooks
git commit -m "message" --no-verify

# Skip specific hooks
SKIP=flake8 git commit -m "message"
```

Note: Bypassing hooks should be done sparingly and with good reason.

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
   npm run start
   ```

2. **Frontend Testing Commands**
   ```bash
   # Test frontend health
   curl http://localhost:3000/
   
   # Test scraping endpoint
   curl -X POST http://localhost:3000/api/scrape \
     -H "Content-Type: application/json" \
     -d '{"urls": ["https://example.com"], "config": {...}}'
   ```

## Docker Environment Setup

### Docker Architecture Overview

The Crawl4AI Scraper application is fully containerized using Docker and orchestrated with Docker Compose. The architecture consists of three main services:

1. **Database Service (`db`)**
   - PostgreSQL 15 database server
   - Stores all application data including credentials, scrape metadata, and scrape results
   - Exposed on host port 5434 (mapped to container port 5432)

2. **Backend Service (`backend`)**
   - FastAPI application serving REST API endpoints
   - Handles scraping requests, database operations, and credential management
   - Exposed on host port 8002
   - Container path structure:
     - `/app`: Application root (contains all code)
     - `/app/data`: Persistent storage for scrape results (mounted from host)
     - `/app/shared`: Shared storage between containers

3. **Frontend Service (`frontend`)**
   - Streamlit web application
   - Provides user interface for scraping operations
   - Exposed on host port 8502
   - Container path structure:
     - `/app`: Application root (contains all code)
     - `/app/data`: Persistent storage for scrape results (mounted from host)
     - `/app/shared`: Shared storage between containers

### Volume Mounts and Data Persistence

The application uses several volume mounts to ensure data persistence:

1. **`postgres_data`** (Docker volume)
   - Purpose: Stores PostgreSQL database files
   - Mount point: `/var/lib/postgresql/data` in the database container
   - Persists across container restarts and rebuilds

2. **`shared_storage`** (Docker volume)
   - Purpose: Shared storage accessible by both backend and frontend
   - Mount points: 
     - `/app/shared` in the backend container
     - `/app/shared` in the frontend container
   - Used for exchanging data between services

3. **`./data`** (Host directory mount)
   - Purpose: Store scrape results and other persistent data
   - Mount points: 
     - `/app/data` in the backend container
     - `/app/data` in the frontend container
   - Accessible from the host machine at `./data` relative to the project root

### Network Configuration

All services are connected through a dedicated Docker network named `crawl4ai-network`. This network:
- Isolates the application services from other Docker containers on the host
- Enables service discovery using container names as hostnames
- Allows controlled exposure of services to the host via port mapping

### Environment Variables

The application uses environment variables for configuration:

1. **Database Configuration**
   - `POSTGRES_USER`: Database username (default: crawl4ai)
   - `POSTGRES_PASSWORD`: Database password (default: crawl4ai)
   - `POSTGRES_DB`: Database name (default: crawl4ai)
   - `DATABASE_URL`: Full database connection string

2. **Application Configuration**
   - `ENCRYPTION_KEY`: Key used for encrypting sensitive data
   - Additional environment variables can be added in the `environment` section of each service

### Getting Started with Docker

#### Prerequisites
- Docker and Docker Compose installed on your system
- Git repository cloned to your local machine

#### Starting the Application

1. **Set up environment variables**
   Create a `.env` file in the project root with the following variables:
   ```
   POSTGRES_USER=crawl4ai
   POSTGRES_PASSWORD=crawl4ai
   POSTGRES_DB=crawl4ai
   ENCRYPTION_KEY=your_generated_encryption_key
   ```

2. **Build and start the containers**
   ```bash
   docker-compose up -d --build
   ```

3. **Access the application**
   - Frontend UI: http://localhost:8502
   - Backend API: http://localhost:8002
   - API Documentation: http://localhost:8002/docs

#### Managing the Docker Environment

1. **View container logs**
   ```bash
   # View logs for a specific service
   docker logs url_scraper-backend
   docker logs url_scraper-frontend
   docker logs url_scraper-db
   
   # Follow logs in real-time
   docker logs -f url_scraper-backend
   ```

2. **Restart services**
   ```bash
   # Restart a specific service
   docker-compose restart backend
   
   # Restart all services
   docker-compose restart
   ```

3. **Stop the application**
   ```bash
   # Stop all containers
   docker-compose down
   
   # Stop and remove volumes (caution: this will delete all data)
   docker-compose down -v
   ```

4. **Rebuild after code changes**
   ```bash
   # Rebuild and restart all services
   docker-compose up -d --build
   
   # Rebuild a specific service
   docker-compose up -d --build backend
   ```

### Troubleshooting Docker Issues

1. **Database Connection Issues**
   - Ensure the database container is healthy: `docker ps` should show "healthy" status
   - Check that the backend is using `db:5432` as the database host, not localhost
   - Verify database credentials in the `.env` file

2. **Container Startup Failures**
   - Check container logs: `docker logs url_scraper-backend`
   - Ensure all required environment variables are set
   - Verify that ports are not already in use on the host

3. **Volume Permission Issues**
   - Ensure the `./data` directory has appropriate permissions
   - If using Linux, you may need to adjust ownership: `sudo chown -R $(id -u):$(id -g) ./data`

4. **Network Connectivity Issues**
   - Ensure all services are on the same network: `docker network inspect url_scraper-network`
   - Check that service names are used for inter-container communication, not localhost

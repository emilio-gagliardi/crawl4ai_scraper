# Docker Setup for Crawl4AI Scraper

This directory contains the Docker configuration for the Crawl4AI Scraper project.

## Services

The Docker setup consists of three services:

1. **Database (PostgreSQL)**
   - Container name: `crawl4ai-db`
   - Port mapping: `5434:5432`
   - Data stored in a persistent volume: `postgres_data`

2. **Backend (FastAPI)**
   - Container name: `crawl4ai-backend`
   - Port mapping: `8002:8002`
   - Built from `docker/backend/Dockerfile`
   - Depends on the database service

3. **Frontend (Streamlit)**
   - Container name: `crawl4ai-frontend`
   - Port mapping: `8502:8502`
   - Built from `docker/frontend/Dockerfile`
   - Depends on the backend service

## Shared Storage

All services have access to two shared volumes:
- `./data:/app/data`: Project-specific data volume
- `shared_storage`: Docker volume for inter-service file sharing

## Networking

All services are connected via a custom bridge network called `crawl4ai-network`.

## Secure Credential Management

The project supports two approaches for managing sensitive credentials:

### Development Environment

For development, use environment variables through a `.env` file:

1. Copy `.env.example` to `.env` in the project root
2. Update the values in the `.env` file with your credentials
3. Run `docker-compose up -d`

The `.env` file should never be committed to source control.

### Production Environment

For production, use Docker Secrets:

1. Run the `setup_secrets.ps1` (Windows) or `setup_secrets.sh` (Unix) script
2. Update the values in the generated secret files in the `secrets` directory
3. Run `docker-compose -f docker-compose.prod.yml up -d`

The `secrets` directory should never be committed to source control.

## Getting Started

### Development Setup

1. Copy `.env.example` to `.env` in the project root and update the values
2. Run `docker-compose up -d` to start all services
3. Access the frontend at `http://localhost:8502`
4. Access the backend API at `http://localhost:8002`

### Production Setup

1. Run `./setup_secrets.sh` (or `.\setup_secrets.ps1` on Windows)
2. Update the secret files in the `secrets` directory
3. Run `docker-compose -f docker-compose.prod.yml up -d`
4. Access the frontend at `http://localhost:8502`
5. Access the backend API at `http://localhost:8002`

## Troubleshooting

- To view logs: `docker-compose logs -f [service_name]`
- To restart a service: `docker-compose restart [service_name]`
- To rebuild a service: `docker-compose up -d --build [service_name]`

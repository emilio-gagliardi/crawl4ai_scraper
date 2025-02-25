from setuptools import find_packages, setup

setup(
    name="crawl4ai_scraper",
    version="0.1.0",
    description="AI-powered web scraping tool",
    author="Emilio Gagliardi",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "sqlmodel>=0.0.14",
        "alembic>=1.13.1",
        "psycopg2-binary>=2.9.9",
        "python-dotenv>=1.0.0",
        "pydantic>=2.5.2",
        "cryptography>=41.0.7",
        "playwright>=1.41.2",
        "beautifulsoup4>=4.12.2",
        "openai>=1.3.7",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.23.5",
            "httpx>=0.26.0",
            "black>=24.1.1",
            "isort>=5.13.2",
            "flake8>=7.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "crawl4ai=crawl4ai_scraper.main:app",
        ],
    },
)

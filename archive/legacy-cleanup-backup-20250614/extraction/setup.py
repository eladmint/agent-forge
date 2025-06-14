from setuptools import find_packages, setup

setup(
    name="nuru-ai-extraction",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4>=4.12.0",
        "selenium>=4.11.0",
        "requests>=2.31.0",
        "httpx>=0.27.0",
        "pydantic>=2.8.0",
        "python-dotenv>=1.0.0",
        "supabase>=1.0.0",
        "anyio>=1.4.0",
        "python-dateutil>=2.9.0",
        "pytz>=2024.1",
        "lxml>=4.9.0",
        "aiohttp>=3.8.0",
        "redis>=5.0.0",
    ],
    entry_points={
        "console_scripts": [
            "nuru-extraction=extraction.main:main",
        ],
    },
    python_requires=">=3.10",
    description="Nuru AI Extraction Service - Web scraping and data extraction for Web3 events",
    author="Nuru AI Team",
    license="MIT",
)

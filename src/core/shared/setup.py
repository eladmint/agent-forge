from setuptools import find_packages, setup

setup(
    name="agent-forge-shared",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "google-generativeai>=0.8.5",
        "python-dotenv>=1.0.0",
        "supabase>=2.3.1",
        "httpx>=0.27.0",
        "pytz>=2024.1",
        "python-dateutil>=2.9.0",
        "protobuf>=4.25.3",
        "google-cloud-aiplatform>=1.45.0",
        "pydantic>=2.8.0",
        "anyio>=1.4.0",
        "redis>=5.0.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
    ],
    python_requires=">=3.10",
    description="Agent Forge Shared Utilities - Common utilities and configurations for all services",
    author="Agent Forge Team",
    license="MIT",
)

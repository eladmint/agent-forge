"""
PyTest configuration and shared fixtures for Agent Forge tests.
"""

import sys
import pytest
import asyncio
import logging
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any

# Add project root to Python path
project_root = Path(__file__).parent.parent
src_root = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_root))

# Import framework components
from core.agents.base import BaseAgent
from core.shared.web.browsers import SteelBrowserClient



@pytest.fixture
def mock_browser_response():
    """Mock browser response for testing."""
    return {
        "success": True,
        "page_title": "Test Page Title",
        "content": "<html><body><h1>Test Content</h1><p>This is test content for agent testing.</p></body></html>",
        "status": "200",
        "url": "https://example.com"
    }


@pytest.fixture
def mock_browser_client():
    """Mock SteelBrowserClient for testing."""
    mock_client = AsyncMock(spec=SteelBrowserClient)
    
    # Configure default responses
    mock_client.navigate.return_value = {
        "success": True,
        "page_title": "Test Page",
        "content": "<html><body>Test content</body></html>",
        "status": "200"
    }
    
    return mock_client


@pytest.fixture
def sample_config():
    """Sample configuration for testing agents."""
    return {
        "timeout": 30,
        "retries": 3,
        "debug": True,
        "test_mode": True
    }


@pytest.fixture
def test_urls():
    """Sample URLs for testing different agent scenarios."""
    return {
        "simple": "https://example.com",
        "github": "https://github.com/microsoft/vscode",
        "news": "https://news.ycombinator.com",
        "blockchain": "https://cardano.org",
        "complex": "https://api.complex-site.com/data"
    }


@pytest.fixture
def test_tasks():
    """Sample task descriptions for testing."""
    return {
        "simple": "Simple web page analysis",
        "analysis": "Comprehensive data analysis",
        "monitoring": "Monitor content changes",
        "blockchain": "Blockchain proof-of-execution",
        "complex": "Complex multi-step task execution"
    }


@pytest.fixture
def setup_test_logging():
    """Configure logging for tests."""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger("agent_forge.tests")


class MockAgent(BaseAgent):
    """Mock agent for testing BaseAgent functionality."""
    
    def __init__(self, name="test_agent", config=None, **kwargs):
        super().__init__(name, config)
        self.test_data = kwargs
        self.run_called = False
        self.initialize_called = False
        self.cleanup_called = False
    
    async def run(self, *args, **kwargs):
        """Mock run method."""
        self.run_called = True
        return {"status": "success", "data": "test_result"}
    
    async def _initialize(self):
        """Mock initialization."""
        self.initialize_called = True
        return True
    
    async def _cleanup(self):
        """Mock cleanup."""
        self.cleanup_called = True


@pytest.fixture
def mock_agent_class():
    """Mock agent class for testing."""
    return MockAgent


@pytest.fixture
def project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def examples_dir(project_root):
    """Get the examples directory path."""
    return project_root / "examples"


@pytest.fixture
def docs_dir(project_root):
    """Get the documentation directory path."""
    return project_root / "docs"


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "network: mark test as requiring network access"
    )
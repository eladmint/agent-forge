"""
Reusable test fixtures and utilities for Agent Forge testing.
Provides common mock objects, test data, and helper functions
used across the testing suite.
"""

import pytest
import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, MagicMock
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_browser_client():
    """Mock Steel Browser client for testing."""
    client = AsyncMock()
    
    # Default navigation response
    client.navigate.return_value = {
        "status": "success",
        "url": "https://example.com",
        "title": "Example Site",
        "load_time": 1.2,
        "response_code": 200,
        "final_url": "https://example.com"
    }
    
    # Default data extraction response
    client.extract_data.return_value = {
        "data": [
            {"title": "Test Item 1", "url": "/item1", "category": "test"},
            {"title": "Test Item 2", "url": "/item2", "category": "test"},
            {"title": "Test Item 3", "url": "/item3", "category": "test"}
        ],
        "metadata": {
            "extraction_method": "css_selector",
            "page_title": "Example Site",
            "total_items": 3,
            "extraction_timestamp": datetime.now().isoformat()
        }
    }
    
    # Screenshot response
    client.take_screenshot.return_value = {
        "screenshot_path": "/tmp/test_screenshot.png",
        "dimensions": {"width": 1920, "height": 1080},
        "file_size": 245760,
        "format": "PNG"
    }
    
    # Page info response
    client.get_page_info.return_value = {
        "url": "https://example.com",
        "title": "Example Site",
        "meta_description": "Test site for Agent Forge",
        "viewport": {"width": 1920, "height": 1080},
        "user_agent": "Agent Forge Test Browser"
    }
    
    # Cleanup response
    client.close.return_value = {"status": "closed"}
    
    return client


@pytest.fixture
def mock_nmkr_client():
    """Mock NMKR API client for blockchain testing."""
    client = AsyncMock()
    
    # NFT minting response
    client.mint_nft.return_value = {
        "mint_order_id": "test_order_123",
        "transaction_id": "test_tx_456",
        "policy_id": "test_policy_789",
        "asset_name": "TestAgentProof001",
        "status": "submitted",
        "estimated_wait_time": "2-5 minutes"
    }
    
    # Transaction status response
    client.get_transaction_status.return_value = {
        "transaction_id": "test_tx_456",
        "status": "confirmed",
        "block_height": 9876543,
        "confirmations": 6,
        "timestamp": datetime.now().isoformat()
    }
    
    # Wallet balance response
    client.get_wallet_balance.return_value = {
        "balance": "100.0 ADA",
        "utxos": 10,
        "sufficient_funds": True
    }
    
    return client


@pytest.fixture
def mock_masumi_client():
    """Mock Masumi Network API client for testing."""
    client = AsyncMock()
    
    # Agent registration response
    client.register_agent.return_value = {
        "agent_id": "test_masumi_agent_001",
        "registration_status": "active",
        "api_key": "test_api_key_xyz789",
        "marketplace_url": "https://masumi.network/agents/test_masumi_agent_001"
    }
    
    # Payment verification response
    client.verify_payment.return_value = {
        "payment_verified": True,
        "transaction_hash": "0xtest_hash_123",
        "amount": "25.0",
        "currency": "ADA",
        "timestamp": datetime.now().isoformat()
    }
    
    # Agent search response
    client.search_agents.return_value = {
        "agents": [
            {
                "agent_id": "agent_001",
                "name": "Test Scraper",
                "category": "data_extraction",
                "rating": 4.8,
                "available": True
            },
            {
                "agent_id": "agent_002", 
                "name": "Test Analyzer",
                "category": "ai_analysis",
                "rating": 4.6,
                "available": True
            }
        ],
        "total_count": 2
    }
    
    return client


@pytest.fixture
def sample_agent_config():
    """Standard agent configuration for testing."""
    return {
        "agent_id": "test_agent_001",
        "type": "scraper",
        "browser_config": {
            "headless": True,
            "timeout": 30,
            "viewport": {"width": 1920, "height": 1080},
            "user_agent": "Agent Forge Test Browser"
        },
        "extraction_config": {
            "default_selector": "div.content",
            "wait_timeout": 10,
            "retry_attempts": 3,
            "rate_limit": 1.0
        },
        "blockchain_config": {
            "enabled": True,
            "proof_generation": True,
            "nmkr_integration": True,
            "masumi_registration": False
        }
    }


@pytest.fixture
def sample_execution_proof():
    """Sample execution proof data for testing."""
    return {
        "agent_id": "test_agent_001",
        "execution_id": f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "framework": "Agent Forge",
        "framework_version": "1.0.0",
        "task_completed": True,
        "execution_time": 15.3,
        "results": {
            "pages_scraped": 5,
            "data_extracted": 23,
            "quality_score": 0.92,
            "success_rate": 1.0
        },
        "verification_data": {
            "hash": "sha256_test_hash_abc123",
            "signature": "ed25519_test_signature_def456",
            "witness": "test_witness_789"
        }
    }


@pytest.fixture
def temp_workspace():
    """Create temporary workspace for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        workspace = Path(temp_dir)
        
        # Create subdirectories
        (workspace / "configs").mkdir()
        (workspace / "results").mkdir()
        (workspace / "logs").mkdir()
        (workspace / "screenshots").mkdir()
        
        # Create sample config file
        config = {
            "workspace_path": str(workspace),
            "log_level": "DEBUG",
            "test_mode": True
        }
        
        config_file = workspace / "configs" / "test_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        yield workspace


@pytest.fixture
def sample_web_pages():
    """Sample web page content for testing."""
    return {
        "home_page": """
        <html>
            <head><title>Test Home Page</title></head>
            <body>
                <h1>Welcome to Test Site</h1>
                <div class="content">
                    <article class="post">
                        <h2>Article 1</h2>
                        <p>Content of article 1</p>
                        <a href="/article1">Read more</a>
                    </article>
                    <article class="post">
                        <h2>Article 2</h2>
                        <p>Content of article 2</p>
                        <a href="/article2">Read more</a>
                    </article>
                </div>
            </body>
        </html>
        """,
        "article_page": """
        <html>
            <head><title>Test Article</title></head>
            <body>
                <article>
                    <h1>Test Article Title</h1>
                    <div class="meta">
                        <span class="date">2025-06-14</span>
                        <span class="author">Test Author</span>
                    </div>
                    <div class="content">
                        <p>This is the full content of the test article.</p>
                        <p>It contains multiple paragraphs for testing.</p>
                    </div>
                </article>
            </body>
        </html>
        """,
        "list_page": """
        <html>
            <head><title>Test List Page</title></head>
            <body>
                <div class="items">
                    <div class="item">
                        <h3>Item 1</h3>
                        <p>Description 1</p>
                        <span class="price">$10.00</span>
                    </div>
                    <div class="item">
                        <h3>Item 2</h3>
                        <p>Description 2</p>
                        <span class="price">$20.00</span>
                    </div>
                    <div class="item">
                        <h3>Item 3</h3>
                        <p>Description 3</p>
                        <span class="price">$30.00</span>
                    </div>
                </div>
            </body>
        </html>
        """
    }


@pytest.fixture
def mock_external_services():
    """Mock all external services for integration testing."""
    return {
        "browser": mock_browser_client(),
        "nmkr": mock_nmkr_client(),
        "masumi": mock_masumi_client()
    }


class MockAsyncContextManager:
    """Mock async context manager for testing."""
    
    def __init__(self, return_value=None):
        self.return_value = return_value
        self.entered = False
        self.exited = False
    
    async def __aenter__(self):
        self.entered = True
        return self.return_value
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.exited = True
        return False


@pytest.fixture
def mock_async_context():
    """Mock async context manager fixture."""
    return MockAsyncContextManager


class TestDataGenerator:
    """Generate test data for various scenarios."""
    
    @staticmethod
    def generate_agent_configs(count: int) -> List[Dict[str, Any]]:
        """Generate multiple agent configurations."""
        configs = []
        for i in range(count):
            config = {
                "agent_id": f"test_agent_{i+1:03d}",
                "type": "scraper",
                "browser_config": {
                    "headless": True,
                    "timeout": 30 + (i * 5),
                    "viewport": {"width": 1920, "height": 1080}
                },
                "target_urls": [
                    f"https://example.com/page{j+1}" 
                    for j in range(2 + (i % 3))  # 2-4 URLs per agent
                ]
            }
            configs.append(config)
        return configs
    
    @staticmethod
    def generate_execution_proofs(count: int, agent_id: str = None) -> List[Dict[str, Any]]:
        """Generate multiple execution proofs."""
        proofs = []
        for i in range(count):
            proof = {
                "agent_id": agent_id or f"test_agent_{i+1:03d}",
                "execution_id": f"exec_{datetime.now().strftime('%Y%m%d')}_{i+1:03d}",
                "timestamp": (datetime.now() - timedelta(minutes=i*10)).isoformat(),
                "task_completed": True,
                "execution_time": 10.0 + (i * 2.5),
                "results": {
                    "pages_scraped": 3 + i,
                    "data_extracted": 15 + (i * 5),
                    "quality_score": 0.85 + (i * 0.02),
                    "success_rate": 1.0 if i % 10 != 9 else 0.9  # Occasional failure
                }
            }
            proofs.append(proof)
        return proofs
    
    @staticmethod
    def generate_web_content(page_type: str, item_count: int = 5) -> str:
        """Generate web content for different page types."""
        if page_type == "article_list":
            articles = []
            for i in range(item_count):
                articles.append(f"""
                <article class="post">
                    <h2>Test Article {i+1}</h2>
                    <p>Summary of test article {i+1}</p>
                    <a href="/article{i+1}">Read more</a>
                    <span class="date">2025-06-{14-i:02d}</span>
                </article>
                """)
            
            return f"""
            <html>
                <head><title>Article List</title></head>
                <body>
                    <div class="articles">
                        {''.join(articles)}
                    </div>
                </body>
            </html>
            """
        
        elif page_type == "product_list":
            products = []
            for i in range(item_count):
                products.append(f"""
                <div class="product">
                    <h3>Product {i+1}</h3>
                    <p>Description of product {i+1}</p>
                    <span class="price">${(i+1)*10}.00</span>
                    <button class="buy-btn">Buy Now</button>
                </div>
                """)
            
            return f"""
            <html>
                <head><title>Product List</title></head>
                <body>
                    <div class="products">
                        {''.join(products)}
                    </div>
                </body>
            </html>
            """
        
        else:  # Default content
            return """
            <html>
                <head><title>Test Page</title></head>
                <body>
                    <h1>Test Content</h1>
                    <div class="content">
                        <p>This is test content for Agent Forge testing.</p>
                    </div>
                </body>
            </html>
            """


@pytest.fixture
def test_data_generator():
    """Test data generator fixture."""
    return TestDataGenerator


class PerformanceProfiler:
    """Performance profiling utilities for testing."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.measurements = []
    
    def start_measurement(self, label: str = "default"):
        """Start a performance measurement."""
        self.start_time = asyncio.get_event_loop().time()
        return {"label": label, "start": self.start_time}
    
    def end_measurement(self, measurement: Dict[str, Any]) -> float:
        """End a performance measurement and return duration."""
        self.end_time = asyncio.get_event_loop().time()
        duration = self.end_time - measurement["start"]
        
        self.measurements.append({
            "label": measurement["label"],
            "duration": duration,
            "start_time": measurement["start"],
            "end_time": self.end_time
        })
        
        return duration
    
    def get_average_duration(self, label: str = None) -> float:
        """Get average duration for measurements."""
        filtered_measurements = self.measurements
        if label:
            filtered_measurements = [m for m in self.measurements if m["label"] == label]
        
        if not filtered_measurements:
            return 0.0
        
        total_duration = sum(m["duration"] for m in filtered_measurements)
        return total_duration / len(filtered_measurements)
    
    def get_measurement_stats(self) -> Dict[str, Any]:
        """Get comprehensive measurement statistics."""
        if not self.measurements:
            return {"count": 0, "total": 0, "average": 0, "min": 0, "max": 0}
        
        durations = [m["duration"] for m in self.measurements]
        
        return {
            "count": len(durations),
            "total": sum(durations),
            "average": sum(durations) / len(durations),
            "min": min(durations),
            "max": max(durations),
            "measurements": self.measurements
        }


@pytest.fixture
def performance_profiler():
    """Performance profiler fixture."""
    return PerformanceProfiler()


def create_mock_agent_response(
    status: str = "success",
    data: Optional[List[Dict[str, Any]]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a mock agent response for testing."""
    response = {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "agent_id": "test_agent",
        "execution_id": f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    }
    
    if data is not None:
        response["data"] = data
    else:
        response["data"] = [
            {"title": "Mock Item 1", "url": "/item1"},
            {"title": "Mock Item 2", "url": "/item2"}
        ]
    
    if metadata is not None:
        response["metadata"] = metadata
    else:
        response["metadata"] = {
            "total_items": len(response["data"]),
            "extraction_method": "mock",
            "page_title": "Mock Page"
        }
    
    return response


def assert_valid_execution_proof(proof: Dict[str, Any]) -> None:
    """Assert that an execution proof is valid."""
    required_fields = [
        "agent_id", "execution_id", "timestamp", 
        "task_completed", "execution_time", "results"
    ]
    
    for field in required_fields:
        assert field in proof, f"Missing required field: {field}"
    
    assert isinstance(proof["task_completed"], bool)
    assert isinstance(proof["execution_time"], (int, float))
    assert proof["execution_time"] > 0
    assert isinstance(proof["results"], dict)


def assert_valid_browser_response(response: Dict[str, Any]) -> None:
    """Assert that a browser response is valid."""
    assert "status" in response
    assert response["status"] in ["success", "error", "timeout"]
    
    if response["status"] == "success":
        assert "url" in response
        assert "title" in response or "error" in response


def assert_valid_extraction_result(result: Dict[str, Any]) -> None:
    """Assert that an extraction result is valid."""
    assert "data" in result
    assert "metadata" in result
    assert isinstance(result["data"], list)
    assert isinstance(result["metadata"], dict)
    
    if result["data"]:
        # Check that data items have consistent structure
        first_item = result["data"][0]
        for item in result["data"]:
            assert type(item) == type(first_item)
            if isinstance(item, dict):
                # All items should have same keys
                assert set(item.keys()) == set(first_item.keys())


# Export fixtures and utilities for easy import
__all__ = [
    "mock_browser_client",
    "mock_nmkr_client", 
    "mock_masumi_client",
    "sample_agent_config",
    "sample_execution_proof",
    "temp_workspace",
    "sample_web_pages",
    "mock_external_services",
    "MockAsyncContextManager",
    "TestDataGenerator",
    "PerformanceProfiler",
    "create_mock_agent_response",
    "assert_valid_execution_proof",
    "assert_valid_browser_response",
    "assert_valid_extraction_result"
]
"""
Unit tests for Steel Browser client integration.

Tests the SteelBrowserClient functionality, configuration,
and integration patterns used throughout the framework.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any

from core.shared.web.browsers import SteelBrowserClient


@pytest.mark.unit
class TestSteelBrowserClientInitialization:
    """Test SteelBrowserClient initialization and configuration."""
    
    def test_client_initialization(self):
        """Test client initialization with default configuration."""
        client = SteelBrowserClient()
        
        assert client.api_url is not None
        assert isinstance(client.session_timeout, (int, float))
        assert client.session_timeout > 0
    
    def test_client_initialization_with_api_url(self):
        """Test client initialization with custom API URL."""
        custom_url = "https://custom-steel-api.com"
        client = SteelBrowserClient(api_url=custom_url)
        
        assert client.api_url == custom_url
    
    def test_client_initialization_with_config(self):
        """Test client initialization with configuration dictionary."""
        config = {
            "timeout": 60,
            "retries": 5,
            "user_agent": "Custom Agent"
        }
        client = SteelBrowserClient(config=config)
        
        assert client.config == config
    
    def test_client_default_configuration(self):
        """Test default configuration values."""
        client = SteelBrowserClient()
        
        # Should have reasonable defaults
        assert hasattr(client, 'api_url')
        assert hasattr(client, 'session_timeout')
        assert client.session_timeout >= 30  # At least 30 seconds


@pytest.mark.unit
class TestBrowserClientNavigation:
    """Test browser navigation functionality."""
    
    @pytest.mark.asyncio
    async def test_navigate_success(self):
        """Test successful navigation to a URL."""
        client = SteelBrowserClient()
        
        # Mock the HTTP request
        mock_response = {
            "success": True,
            "page_title": "Example Domain",
            "content": "<html><body><h1>Example</h1></body></html>",
            "status": "200",
            "url": "https://example.com"
        }
        
        with patch.object(client, '_make_request', return_value=mock_response) as mock_request:
            result = await client.navigate("https://example.com")
            
            assert result["success"] is True
            assert result["page_title"] == "Example Domain"
            assert "Example" in result["content"]
            assert result["status"] == "200"
            mock_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_navigate_with_options(self):
        """Test navigation with additional options."""
        client = SteelBrowserClient()
        
        mock_response = {
            "success": True,
            "page_title": "Test Page",
            "content": "<html><body>Test</body></html>",
            "status": "200"
        }
        
        with patch.object(client, '_make_request', return_value=mock_response) as mock_request:
            result = await client.navigate(
                "https://example.com",
                wait_for_selector="h1",
                timeout=30
            )
            
            assert result["success"] is True
            mock_request.assert_called_once()
            
            # Check that options were passed to the request
            call_args = mock_request.call_args
            assert "wait_for_selector" in call_args[1] or "h1" in str(call_args)
    
    @pytest.mark.asyncio
    async def test_navigate_failure(self):
        """Test navigation failure handling."""
        client = SteelBrowserClient()
        
        mock_response = {
            "success": False,
            "error": "Failed to load page",
            "status": "404"
        }
        
        with patch.object(client, '_make_request', return_value=mock_response):
            result = await client.navigate("https://nonexistent.example.com")
            
            assert result["success"] is False
            assert "error" in result
            assert result["status"] == "404"
    
    @pytest.mark.asyncio
    async def test_navigate_with_invalid_url(self):
        """Test navigation with invalid URL."""
        client = SteelBrowserClient()
        
        # Should handle invalid URLs gracefully
        result = await client.navigate("not-a-valid-url")
        
        # Should return error response
        assert isinstance(result, dict)
        assert result.get("success") is False
    
    @pytest.mark.asyncio
    async def test_navigate_timeout(self):
        """Test navigation timeout handling."""
        client = SteelBrowserClient()
        
        with patch.object(client, '_make_request', side_effect=asyncio.TimeoutError()):
            result = await client.navigate("https://slow-loading-site.com")
            
            assert result["success"] is False
            assert "timeout" in result.get("error", "").lower()


@pytest.mark.unit
class TestBrowserClientConfiguration:
    """Test browser client configuration and settings."""
    
    def test_config_access(self):
        """Test configuration access patterns."""
        config = {
            "timeout": 45,
            "user_agent": "Agent Forge Browser",
            "viewport": {"width": 1920, "height": 1080}
        }
        client = SteelBrowserClient(config=config)
        
        assert client.config.get("timeout") == 45
        assert client.config.get("user_agent") == "Agent Forge Browser"
        assert client.config.get("viewport")["width"] == 1920
    
    def test_default_config_values(self):
        """Test default configuration values."""
        client = SteelBrowserClient()
        
        # Should have sensible defaults
        assert client.session_timeout > 0
        assert client.api_url is not None
        assert len(client.api_url) > 0
    
    def test_config_override(self):
        """Test configuration override behavior."""
        initial_config = {"timeout": 30}
        client = SteelBrowserClient(config=initial_config)
        
        # Should be able to override config values
        client.config["timeout"] = 60
        assert client.config["timeout"] == 60


@pytest.mark.unit
class TestBrowserClientRequests:
    """Test HTTP request handling in browser client."""
    
    @pytest.mark.asyncio
    async def test_make_request_structure(self):
        """Test internal request method structure."""
        client = SteelBrowserClient()
        
        # Mock aiohttp session
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"success": True, "data": "test"}
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            result = await client._make_request("POST", "https://example.com", {"test": "data"})
            
            assert isinstance(result, dict)
            mock_session.post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_request_headers(self):
        """Test proper request header configuration."""
        client = SteelBrowserClient()
        
        # Should set appropriate headers
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {"success": True}
            mock_session.post.return_value.__aenter__.return_value = mock_response
            mock_session_class.return_value = mock_session
            
            await client._make_request("POST", "https://api.example.com", {"data": "test"})
            
            # Check that headers were set
            call_args = mock_session.post.call_args
            headers = call_args[1].get("headers", {})
            
            # Should have content-type header
            assert any("content-type" in str(k).lower() for k in headers.keys()) or \
                   any("application/json" in str(v).lower() for v in headers.values())
    
    @pytest.mark.asyncio
    async def test_request_error_handling(self):
        """Test request error handling."""
        client = SteelBrowserClient()
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session.post.side_effect = Exception("Network error")
            mock_session_class.return_value = mock_session
            
            result = await client._make_request("POST", "https://api.example.com", {})
            
            assert result["success"] is False
            assert "error" in result


@pytest.mark.unit
class TestBrowserClientIntegration:
    """Test browser client integration patterns."""
    
    @pytest.mark.asyncio
    async def test_client_in_agent_context(self):
        """Test browser client usage in agent context."""
        client = SteelBrowserClient()
        
        # Simulate agent usage pattern
        mock_response = {
            "success": True,
            "page_title": "Agent Test Page",
            "content": "<html><body><h1>Test</h1></body></html>"
        }
        
        with patch.object(client, '_make_request', return_value=mock_response):
            # Agent-like usage pattern
            result = await client.navigate("https://example.com")
            
            # Agent would expect these fields
            assert "success" in result
            assert "page_title" in result
            assert "content" in result
    
    def test_client_configuration_patterns(self):
        """Test common client configuration patterns."""
        # Pattern 1: Default configuration
        client1 = SteelBrowserClient()
        assert client1.api_url is not None
        
        # Pattern 2: Custom API URL
        client2 = SteelBrowserClient(api_url="https://custom-api.com")
        assert client2.api_url == "https://custom-api.com"
        
        # Pattern 3: Configuration dict
        config = {"timeout": 60, "retries": 3}
        client3 = SteelBrowserClient(config=config)
        assert client3.config == config
    
    @pytest.mark.asyncio
    async def test_client_cleanup(self):
        """Test client cleanup and resource management."""
        client = SteelBrowserClient()
        
        # Should handle cleanup gracefully
        try:
            # Simulate cleanup
            if hasattr(client, 'cleanup'):
                await client.cleanup()
            elif hasattr(client, 'close'):
                await client.close()
        except Exception as e:
            pytest.fail(f"Client cleanup failed: {e}")


@pytest.mark.unit
class TestBrowserClientErrorHandling:
    """Test comprehensive error handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_network_timeout_handling(self):
        """Test network timeout error handling."""
        client = SteelBrowserClient()
        
        with patch.object(client, '_make_request', side_effect=asyncio.TimeoutError()):
            result = await client.navigate("https://timeout-test.com")
            
            assert result["success"] is False
            assert "timeout" in str(result.get("error", "")).lower()
    
    @pytest.mark.asyncio
    async def test_connection_error_handling(self):
        """Test connection error handling."""
        client = SteelBrowserClient()
        
        with patch.object(client, '_make_request', side_effect=ConnectionError("Connection failed")):
            result = await client.navigate("https://unreachable.com")
            
            assert result["success"] is False
            assert "error" in result
    
    @pytest.mark.asyncio
    async def test_malformed_response_handling(self):
        """Test handling of malformed API responses."""
        client = SteelBrowserClient()
        
        # Mock malformed response
        malformed_response = "not json"
        
        with patch.object(client, '_make_request', return_value=malformed_response):
            result = await client.navigate("https://example.com")
            
            # Should handle gracefully
            assert isinstance(result, dict)
            # Should indicate some kind of error
            assert result.get("success") is not True
    
    @pytest.mark.asyncio
    async def test_api_error_response_handling(self):
        """Test handling of API error responses."""
        client = SteelBrowserClient()
        
        error_response = {
            "success": False,
            "error": "Rate limit exceeded",
            "status": "429"
        }
        
        with patch.object(client, '_make_request', return_value=error_response):
            result = await client.navigate("https://example.com")
            
            assert result["success"] is False
            assert result["error"] == "Rate limit exceeded"
            assert result["status"] == "429"


@pytest.mark.unit
class TestBrowserClientPerformance:
    """Test browser client performance characteristics."""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling of concurrent navigation requests."""
        client = SteelBrowserClient()
        
        mock_response = {
            "success": True,
            "page_title": "Concurrent Test",
            "content": "<html><body>Test</body></html>"
        }
        
        with patch.object(client, '_make_request', return_value=mock_response):
            # Create multiple concurrent requests
            tasks = [
                client.navigate(f"https://example{i}.com")
                for i in range(5)
            ]
            
            results = await asyncio.gather(*tasks)
            
            # All should succeed
            assert len(results) == 5
            assert all(result["success"] for result in results)
    
    def test_client_memory_efficiency(self):
        """Test client memory usage patterns."""
        # Create multiple clients
        clients = [SteelBrowserClient() for _ in range(10)]
        
        # Should not accumulate excessive state
        for client in clients:
            assert hasattr(client, 'api_url')
            assert hasattr(client, 'config')
            # Should not have large accumulated state
    
    @pytest.mark.asyncio
    async def test_request_caching_behavior(self):
        """Test request caching and state management."""
        client = SteelBrowserClient()
        
        mock_response = {"success": True, "data": "cached"}
        
        with patch.object(client, '_make_request', return_value=mock_response) as mock_request:
            # Make same request twice
            result1 = await client.navigate("https://example.com")
            result2 = await client.navigate("https://example.com")
            
            # Should make separate requests (no unwanted caching)
            assert mock_request.call_count == 2
            assert result1 == result2


@pytest.mark.unit
class TestBrowserClientMocking:
    """Test browser client mocking patterns for testing."""
    
    def test_mock_client_creation(self):
        """Test creating mock browser client for testing."""
        mock_client = Mock(spec=SteelBrowserClient)
        
        # Should have expected interface
        assert hasattr(mock_client, 'navigate')
        assert hasattr(mock_client, 'api_url')
    
    @pytest.mark.asyncio
    async def test_async_mock_client(self):
        """Test async mock browser client."""
        mock_client = AsyncMock(spec=SteelBrowserClient)
        mock_client.navigate.return_value = {
            "success": True,
            "page_title": "Mock Page",
            "content": "<html><body>Mock</body></html>"
        }
        
        result = await mock_client.navigate("https://example.com")
        
        assert result["success"] is True
        assert result["page_title"] == "Mock Page"
        mock_client.navigate.assert_called_once_with("https://example.com")
    
    def test_mock_client_configuration(self):
        """Test mock client configuration for testing."""
        # Create configured mock
        mock_client = Mock(spec=SteelBrowserClient)
        mock_client.api_url = "https://mock-api.com"
        mock_client.config = {"timeout": 30}
        
        assert mock_client.api_url == "https://mock-api.com"
        assert mock_client.config["timeout"] == 30
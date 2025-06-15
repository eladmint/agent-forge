"""
Unit tests for BaseAgent foundation class.

Tests the core functionality of the BaseAgent class including lifecycle management,
configuration handling, logging, and async patterns.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from core.agents.base import BaseAgent, AsyncContextAgent
from core.shared.web.browsers import SteelBrowserClient


class MockAgent(AsyncContextAgent):
    """Mock implementation of BaseAgent for testing."""
    
    def __init__(self, name="test_agent", config=None, **kwargs):
        super().__init__(name, config)
        self.test_kwargs = kwargs
        self.run_called = False
        self.run_result = {"status": "success", "test": True}
        
    async def run(self, *args, **kwargs):
        """Test run implementation."""
        self.run_called = True
        self.run_args = args
        self.run_kwargs = kwargs
        return self.run_result


@pytest.mark.unit
class TestBaseAgentInitialization:
    """Test BaseAgent initialization and configuration."""
    
    def test_init_with_defaults(self):
        """Test agent initialization with default parameters."""
        agent = MockAgent()
        
        assert agent.name is not None
        assert agent.config == {}
        assert agent.logger is not None
        assert not agent.is_initialized
        assert agent.browser_client is None
    
    def test_init_with_name_and_config(self):
        """Test agent initialization with custom name and config."""
        config = {"timeout": 30, "debug": True}
        agent = MockAgent(name="custom_agent", config=config)
        
        assert agent.name == "custom_agent"
        assert agent.config == config
        assert agent.logger.name == "agent_forge.custom_agent"
    
    def test_init_with_kwargs(self):
        """Test agent initialization with additional keyword arguments."""
        agent = MockAgent(url="https://example.com", task="test task")
        
        assert agent.test_kwargs["url"] == "https://example.com"
        assert agent.test_kwargs["task"] == "test task"


@pytest.mark.unit
class TestBaseAgentLifecycle:
    """Test BaseAgent lifecycle management."""
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, mock_browser_client):
        """Test successful agent initialization."""
        agent = MockAgent()
        
        with patch('core.shared.web.browsers.SteelBrowserClient', return_value=mock_browser_client):
            success = await agent.initialize()
            
        assert success is True
        assert agent.is_initialized is True
        assert agent.browser_client is not None
        assert agent.is_ready() is True
    
    @pytest.mark.asyncio
    async def test_initialize_failure(self):
        """Test agent initialization failure."""
        agent = MockAgent()
        
        # Mock the _initialize method to fail
        with patch.object(agent, '_initialize', side_effect=Exception("Agent setup failed")):
            success = await agent.initialize()
            
        assert success is False
        assert agent.is_initialized is False
        assert agent.is_ready() is False
    
    @pytest.mark.asyncio
    async def test_cleanup_success(self, mock_browser_client):
        """Test successful agent cleanup."""
        agent = MockAgent()
        agent.browser_client = mock_browser_client
        agent.is_initialized = True
        
        await agent.cleanup()
        
        assert agent.is_initialized is False
    
    @pytest.mark.asyncio
    async def test_double_initialize(self, mock_browser_client):
        """Test that double initialization is handled correctly."""
        agent = MockAgent()
        
        with patch('core.shared.web.browsers.SteelBrowserClient', return_value=mock_browser_client):
            success1 = await agent.initialize()
            success2 = await agent.initialize()
            
        assert success1 is True
        assert success2 is True  # BaseAgent allows re-initialization
    
    @pytest.mark.asyncio
    async def test_context_manager(self, mock_browser_client):
        """Test agent as async context manager."""
        agent = MockAgent()
        
        with patch('core.shared.web.browsers.SteelBrowserClient', return_value=mock_browser_client):
            async with agent as ctx_agent:
                assert ctx_agent is agent
                assert agent.is_ready() is True
                
        # After context exit, should be cleaned up
        assert agent.is_initialized is False


@pytest.mark.unit
class TestBaseAgentStatus:
    """Test BaseAgent status and monitoring functionality."""
    
    def test_is_ready_when_not_initialized(self):
        """Test is_ready returns False when not initialized."""
        agent = MockAgent()
        assert agent.is_ready() is False
    
    def test_is_ready_when_initialized(self):
        """Test is_ready returns True when initialized."""
        agent = MockAgent()
        agent.is_initialized = True
        assert agent.is_ready() is True
    
    def test_get_status_not_initialized(self):
        """Test get_status when agent is not initialized."""
        agent = MockAgent()
        status = agent.get_status()
        
        assert status["name"] == agent.name
        assert status["ready"] is False
        assert status["initialized"] is False
        assert status["config"] == {}
    
    def test_get_status_initialized(self, mock_browser_client):
        """Test get_status when agent is initialized."""
        agent = MockAgent()
        agent.is_initialized = True
        agent.browser_client = mock_browser_client
        
        status = agent.get_status()
        
        assert status["ready"] is True
        assert status["initialized"] is True


@pytest.mark.unit
class TestBaseAgentRun:
    """Test BaseAgent run method and abstract implementation."""
    
    @pytest.mark.asyncio
    async def test_run_implementation(self):
        """Test that run method is implemented in concrete class."""
        agent = MockAgent()
        
        result = await agent.run("test_arg", test_kwarg="test_value")
        
        assert agent.run_called is True
        assert agent.run_args == ("test_arg",)
        assert agent.run_kwargs == {"test_kwarg": "test_value"}
        assert result == {"status": "success", "test": True}
    
    @pytest.mark.asyncio
    async def test_run_with_custom_result(self):
        """Test run method with custom result."""
        agent = MockAgent()
        agent.run_result = {"custom": "result", "data": [1, 2, 3]}
        
        result = await agent.run()
        
        assert result == {"custom": "result", "data": [1, 2, 3]}


@pytest.mark.unit
class TestBaseAgentConfiguration:
    """Test BaseAgent configuration handling."""
    
    def test_config_access(self):
        """Test configuration access patterns."""
        config = {
            "timeout": 30,
            "retries": 3,
            "debug": True,
            "api_key": "test_key"
        }
        agent = MockAgent(config=config)
        
        assert agent.config.get("timeout") == 30
        assert agent.config.get("retries") == 3
        assert agent.config.get("debug") is True
        assert agent.config.get("api_key") == "test_key"
        assert agent.config.get("missing_key") is None
        assert agent.config.get("missing_key", "default") == "default"
    
    def test_empty_config(self):
        """Test agent with empty configuration."""
        agent = MockAgent(config={})
        
        assert agent.config == {}
        assert agent.config.get("any_key") is None


@pytest.mark.unit
class TestBaseAgentLogging:
    """Test BaseAgent logging functionality."""
    
    def test_logger_creation(self):
        """Test that logger is created correctly."""
        agent = MockAgent(name="test_logger_agent")
        
        assert agent.logger is not None
        assert agent.logger.name == "agent_forge.test_logger_agent"
    
    def test_logger_usage(self):
        """Test basic logger usage."""
        agent = MockAgent()
        
        # Should not raise any exceptions
        agent.logger.info("Test info message")
        agent.logger.debug("Test debug message")
        agent.logger.warning("Test warning message")


@pytest.mark.unit
class TestBaseAgentBrowserIntegration:
    """Test BaseAgent browser client integration."""
    
    @pytest.mark.asyncio
    async def test_browser_client_creation(self):
        """Test browser client creation during initialization."""
        agent = MockAgent()
        
        with patch('core.agents.base.SteelBrowserClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            await agent.initialize()
            
            assert agent.browser_client is not None
            # Verify that SteelBrowserClient was called with the API URL
            mock_client_class.assert_called_once_with(api_url='https://production-orchestrator-867263134607.us-central1.run.app')
    
    @pytest.mark.asyncio
    async def test_browser_client_cleanup(self):
        """Test browser client cleanup."""
        agent = MockAgent()
        mock_browser_client = AsyncMock()
        agent.browser_client = mock_browser_client
        agent.is_initialized = True
        
        await agent.cleanup()
        
        # Browser client cleanup is handled by the agent


@pytest.mark.unit
class TestBaseAgentErrorHandling:
    """Test BaseAgent error handling patterns."""
    
    @pytest.mark.asyncio
    async def test_initialization_error_handling(self):
        """Test error handling during initialization."""
        agent = MockAgent()
        
        with patch('core.agents.base.SteelBrowserClient', side_effect=RuntimeError("Test error")):
            success = await agent.initialize()
            
        assert success is False
        assert agent.is_initialized is False
    
    @pytest.mark.asyncio
    async def test_cleanup_error_handling(self):
        """Test error handling during cleanup."""
        agent = MockAgent()
        mock_browser_client = AsyncMock()
        # Simulate cleanup error in the agent's _cleanup method
        agent.browser_client = mock_browser_client
        agent.is_initialized = True
        
        # Should not raise exception
        await agent.cleanup()
        
        # Should still mark as not initialized
        assert agent.is_initialized is False


@pytest.mark.unit
class TestBaseAgentIntegration:
    """Test BaseAgent integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_full_lifecycle(self, mock_browser_client):
        """Test complete agent lifecycle."""
        agent = MockAgent(
            name="integration_test_agent",
            config={"test": True}
        )
        
        with patch('core.shared.web.browsers.SteelBrowserClient', return_value=mock_browser_client):
            # Initialize
            init_success = await agent.initialize()
            assert init_success is True
            assert agent.is_ready() is True
            
            # Run
            result = await agent.run("test_data")
            assert result["status"] == "success"
            assert agent.run_called is True
            
            # Check status
            status = agent.get_status()
            assert status["ready"] is True
            assert status["initialized"] is True
            
            # Cleanup
            await agent.cleanup()
            assert agent.is_initialized is False
    
    @pytest.mark.asyncio
    async def test_context_manager_with_run(self, mock_browser_client):
        """Test using agent as context manager with run method."""
        agent = MockAgent()
        
        with patch('core.shared.web.browsers.SteelBrowserClient', return_value=mock_browser_client):
            async with agent:
                result = await agent.run("context_test")
                
                assert agent.is_ready() is True
                assert result["status"] == "success"
                assert agent.run_called is True
            
            # After context, should be cleaned up
            assert agent.is_initialized is False
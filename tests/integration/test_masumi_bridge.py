"""
Masumi Bridge Integration Tests

Tests for the Agent Forge + Masumi Network bridge integration.
Validates the bridge adapter, payment client, and registry integration.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from typing import Dict, Any

from core.shared.masumi import (
    MasumiBridgeAdapter, 
    MasumiAgentWrapper,
    MasumiConfig,
    MasumiPaymentClient,
    MasumiRegistryClient
)
from examples.simple_navigation_agent import SimpleNavigationAgent


class TestMasumiConfig:
    """Test Masumi configuration management."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = MasumiConfig()
        
        assert config.payment_service_url == "https://payment.masumi.network"
        assert config.network == "preprod"
        assert config.payment_bearer_token == "iofsnaiojdoiewqajdriknjonasfoinasd"
        assert config.registry_api_key == "jonasfoinas0dmwrpomopdsad33"
    
    def test_testing_config(self):
        """Test testing configuration setup."""
        config = MasumiConfig.for_testing()
        
        assert config.network == "preprod"
        assert config.validate() == True
    
    def test_production_config(self):
        """Test production configuration setup."""
        with patch.dict('os.environ', {
            'MASUMI_PAYMENT_URL': 'https://prod.masumi.network',
            'MASUMI_NETWORK': 'mainnet'
        }):
            config = MasumiConfig.for_production()
            
            assert config.network == "mainnet"
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Valid config
        config = MasumiConfig()
        assert config.validate() == True
        
        # Invalid config
        config.payment_bearer_token = ""
        assert config.validate() == False


class TestMasumiPaymentClient:
    """Test Masumi payment service integration."""
    
    @pytest.fixture
    def mock_session(self):
        """Mock aiohttp session."""
        session = AsyncMock()
        return session
    
    @pytest.fixture
    def payment_client(self):
        """Create payment client for testing."""
        config = MasumiConfig.for_testing()
        return MasumiPaymentClient(config)
    
    @pytest.mark.asyncio
    async def test_client_initialization(self, payment_client):
        """Test payment client initialization."""
        assert payment_client.config.network == "preprod"
        assert payment_client.session is None
        
        # Test context manager
        async with payment_client as client:
            assert client.session is not None
    
    @pytest.mark.asyncio
    async def test_verify_payment_success(self):
        """Test successful payment verification."""
        config = MasumiConfig.for_testing()
        
        with patch('core.shared.masumi.payment_client.aiohttp.ClientSession') as mock_session_class:
            # Mock the session and its post method
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"verified": True})
            
            # Create proper context manager
            mock_session.post.return_value.__aenter__ = AsyncMock(return_value=mock_response)
            mock_session.post.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_session.close = AsyncMock()
            
            mock_session_class.return_value = mock_session
            
            async with MasumiPaymentClient(config) as client:
                result = await client.verify_payment("test_proof", "job_123")
                
                assert result == True
    
    @pytest.mark.asyncio
    async def test_verify_payment_failure(self):
        """Test failed payment verification."""
        config = MasumiConfig.for_testing()
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            # Mock failed response
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 400
            
            # Create proper context manager
            mock_context_manager = AsyncMock()
            mock_context_manager.__aenter__ = AsyncMock(return_value=mock_response)
            mock_context_manager.__aexit__ = AsyncMock(return_value=None)
            mock_session.post.return_value = mock_context_manager
            mock_session.close = AsyncMock()
            
            mock_session_class.return_value = mock_session
            
            async with MasumiPaymentClient(config) as client:
                result = await client.verify_payment("invalid_proof", "job_123")
                
                assert result == False
    
    @pytest.mark.asyncio
    async def test_create_payment_request(self):
        """Test payment request creation."""
        config = MasumiConfig.for_testing()
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            # Mock successful response
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 201
            mock_response.json = AsyncMock(return_value={
                "payment_address": "addr_test123",
                "amount": 5.0,
                "reference": "ref_123"
            })
            
            # Create proper context manager
            mock_context_manager = AsyncMock()
            mock_context_manager.__aenter__ = AsyncMock(return_value=mock_response)
            mock_context_manager.__aexit__ = AsyncMock(return_value=None)
            mock_session.post.return_value = mock_context_manager
            mock_session.close = AsyncMock()
            
            mock_session_class.return_value = mock_session
            
            async with MasumiPaymentClient(config) as client:
                result = await client.create_payment_request(
                    job_id="job_123",
                    amount_ada=5.0,
                    agent_did="did:cardano:test",
                    service_description="Test service"
                )
                
                assert result["amount"] == 5.0
                assert "payment_address" in result
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test payment service health check."""
        config = MasumiConfig.for_testing()
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            # Mock healthy response
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200
            
            # Create proper context manager
            mock_context_manager = AsyncMock()
            mock_context_manager.__aenter__ = AsyncMock(return_value=mock_response)
            mock_context_manager.__aexit__ = AsyncMock(return_value=None)
            mock_session.get.return_value = mock_context_manager
            mock_session.close = AsyncMock()
            
            mock_session_class.return_value = mock_session
            
            async with MasumiPaymentClient(config) as client:
                result = await client.health_check()
                
                assert result == True


class TestMasumiRegistryClient:
    """Test Masumi registry integration."""
    
    @pytest.fixture
    def registry_client(self):
        """Create registry client for testing."""
        config = MasumiConfig.for_testing()
        return MasumiRegistryClient(config)
    
    @pytest.mark.asyncio
    async def test_register_agent_success(self):
        """Test successful agent registration."""
        config = MasumiConfig.for_testing()
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            # Mock successful response
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 201
            mock_response.json = AsyncMock(return_value={"agent_id": "123", "status": "registered"})
            
            # Create proper context manager
            mock_context_manager = AsyncMock()
            mock_context_manager.__aenter__ = AsyncMock(return_value=mock_response)
            mock_context_manager.__aexit__ = AsyncMock(return_value=None)
            mock_session.post.return_value = mock_context_manager
            mock_session.close = AsyncMock()
            
            mock_session_class.return_value = mock_session
            
            async with MasumiRegistryClient(config) as client:
                result = await client.register_agent(
                    agent_name="TestAgent",
                    agent_did="did:cardano:test",
                    capabilities=["web_navigation"],
                    api_endpoint="https://test.com/api",
                    price_ada=5.0,
                    description="Test agent"
                )
                
                assert result["status"] == "registered"
    
    @pytest.mark.asyncio
    async def test_discover_agents(self):
        """Test agent discovery."""
        config = MasumiConfig.for_testing()
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            # Mock discovery response
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "agents": [
                    {"name": "Agent1", "capabilities": ["web_navigation"]},
                    {"name": "Agent2", "capabilities": ["data_analysis"]}
                ]
            })
            
            # Create proper context manager
            mock_context_manager = AsyncMock()
            mock_context_manager.__aenter__ = AsyncMock(return_value=mock_response)
            mock_context_manager.__aexit__ = AsyncMock(return_value=None)
            mock_session.get.return_value = mock_context_manager
            mock_session.close = AsyncMock()
            
            mock_session_class.return_value = mock_session
            
            async with MasumiRegistryClient(config) as client:
                result = await client.discover_agents(
                    capabilities=["web_navigation"],
                    framework="Agent Forge"
                )
                
                assert len(result) == 2
                assert result[0]["name"] == "Agent1"


class TestMasumiAgentWrapper:
    """Test Agent Forge agent wrapper for Masumi integration."""
    
    @pytest.fixture
    def mock_agent(self):
        """Create mock Agent Forge agent."""
        agent = AsyncMock()
        agent.name = "TestAgent"
        agent.run.return_value = {"title": "Test Page", "success": True}
        return agent
    
    @pytest.fixture
    def agent_wrapper(self, mock_agent):
        """Create agent wrapper for testing."""
        config = MasumiConfig.for_testing()
        return MasumiAgentWrapper(
            agent=mock_agent,
            config=config,
            agent_did="did:cardano:test_agent",
            price_ada=3.0
        )
    
    def test_wrapper_initialization(self, agent_wrapper, mock_agent):
        """Test wrapper initialization."""
        assert agent_wrapper.agent == mock_agent
        assert agent_wrapper.agent_did == "did:cardano:test_agent"
        assert agent_wrapper.price_ada == 3.0
        assert len(agent_wrapper.decision_log) == 0
    
    def test_decision_logging(self, agent_wrapper):
        """Test decision logging functionality."""
        agent_wrapper.log_decision("test_decision", {"key": "value"})
        
        assert len(agent_wrapper.decision_log) == 1
        assert agent_wrapper.decision_log[0]["type"] == "test_decision"
        assert agent_wrapper.decision_log[0]["data"]["key"] == "value"
        assert agent_wrapper.decision_log[0]["agent"] == "TestAgent"
    
    def test_get_capabilities(self, agent_wrapper):
        """Test capability extraction."""
        capabilities = agent_wrapper.get_capabilities()
        
        assert "web_automation" in capabilities
        assert "data_extraction" in capabilities
        assert isinstance(capabilities, list)
    
    def test_get_api_schema(self, agent_wrapper):
        """Test API schema generation."""
        schema = agent_wrapper.get_api_schema()
        
        assert schema["type"] == "object"
        assert "job_id" in schema["properties"]
        assert "job_id" in schema["required"]
    
    @pytest.mark.asyncio
    async def test_generate_execution_proof(self, agent_wrapper):
        """Test execution proof generation."""
        input_data = {"url": "https://test.com"}
        output_data = {"title": "Test", "success": True}
        
        proof = await agent_wrapper.generate_execution_proof(
            input_data=input_data,
            output_data=output_data,
            job_id="job_123",
            requester_did="did:cardano:requester"
        )
        
        assert "proof_hash" in proof
        assert "proof_data" in proof
        assert proof["masumi_compliant"] == True
        assert len(proof["proof_hash"]) == 64  # SHA-256 hash
        
        # Validate proof data structure
        proof_data = proof["proof_data"]
        assert proof_data["job_id"] == "job_123"
        assert proof_data["agent_did"] == "did:cardano:test_agent"
        assert proof_data["input"] == input_data
        assert proof_data["output"] == output_data
        assert proof_data["framework"] == "Agent Forge"
    
    @pytest.mark.asyncio
    async def test_execute_with_masumi_no_payment(self, agent_wrapper, mock_agent):
        """Test execution without payment verification."""
        # Mock agent context manager
        mock_agent.__aenter__ = AsyncMock(return_value=mock_agent)
        mock_agent.__aexit__ = AsyncMock(return_value=None)
        
        result = await agent_wrapper.execute_with_masumi(
            job_id="job_123",
            url="https://test.com"
        )
        
        assert result["job_id"] == "job_123"
        assert result["agent_did"] == "did:cardano:test_agent"
        assert "result" in result
        assert "proof_hash" in result
        assert result["payment_verified"] == True  # No payment proof = auto-verified for testing
        assert result["payment_claimed"] == False
        assert result["execution_time"] > 0
        assert result["decision_count"] > 0
    
    @pytest.mark.asyncio
    async def test_execute_with_masumi_with_payment(self, agent_wrapper, mock_agent):
        """Test execution with payment verification."""
        # Mock payment verification
        with patch('core.shared.masumi.bridge_adapter.MasumiPaymentClient') as mock_payment_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.verify_payment.return_value = True
            mock_client_instance.claim_payment.return_value = "tx_hash_123"
            mock_payment_client.return_value.__aenter__.return_value = mock_client_instance
            
            # Mock agent context manager
            mock_agent.__aenter__ = AsyncMock(return_value=mock_agent)
            mock_agent.__aexit__ = AsyncMock(return_value=None)
            
            result = await agent_wrapper.execute_with_masumi(
                job_id="job_123",
                payment_proof="payment_proof_123",
                requester_did="did:cardano:requester",
                url="https://test.com"
            )
            
            assert result["payment_verified"] == True
            assert result["payment_claimed"] == True
            
            # Verify payment verification was called
            mock_client_instance.verify_payment.assert_called_once_with("payment_proof_123", "job_123")
            mock_client_instance.claim_payment.assert_called_once()


class TestMasumiBridgeAdapter:
    """Test main bridge adapter functionality."""
    
    @pytest.fixture
    def bridge_adapter(self):
        """Create bridge adapter for testing."""
        config = MasumiConfig.for_testing()
        return MasumiBridgeAdapter(config)
    
    @pytest.fixture
    def simple_agent(self):
        """Create simple navigation agent for testing."""
        return SimpleNavigationAgent(url="https://test.com")
    
    def test_adapter_initialization(self, bridge_adapter):
        """Test bridge adapter initialization."""
        assert bridge_adapter.config.network == "preprod"
        assert len(bridge_adapter.registered_agents) == 0
    
    def test_wrap_agent(self, bridge_adapter, simple_agent):
        """Test agent wrapping functionality."""
        wrapper = bridge_adapter.wrap_agent(
            agent=simple_agent,
            agent_did="did:cardano:test",
            price_ada=5.0
        )
        
        assert isinstance(wrapper, MasumiAgentWrapper)
        assert wrapper.agent == simple_agent
        assert wrapper.agent_did == "did:cardano:test"
        assert wrapper.price_ada == 5.0
        
        # Verify agent is registered
        assert len(bridge_adapter.registered_agents) == 1
        assert bridge_adapter.registered_agents["did:cardano:test"] == wrapper
    
    def test_get_wrapped_agent(self, bridge_adapter, simple_agent):
        """Test retrieving wrapped agents."""
        wrapper = bridge_adapter.wrap_agent(simple_agent)
        did = wrapper.agent_did
        
        retrieved = bridge_adapter.get_wrapped_agent(did)
        assert retrieved == wrapper
        
        # Test non-existent agent
        assert bridge_adapter.get_wrapped_agent("non_existent") is None
    
    def test_list_registered_agents(self, bridge_adapter, simple_agent):
        """Test listing registered agents."""
        # Initially empty
        assert len(bridge_adapter.list_registered_agents()) == 0
        
        # Add agents
        wrapper1 = bridge_adapter.wrap_agent(simple_agent, agent_did="did:1")
        wrapper2 = bridge_adapter.wrap_agent(simple_agent, agent_did="did:2")
        
        agent_list = bridge_adapter.list_registered_agents()
        assert len(agent_list) == 2
        assert "did:1" in agent_list
        assert "did:2" in agent_list
    
    @pytest.mark.asyncio
    async def test_register_agent_with_masumi(self, bridge_adapter, simple_agent):
        """Test registering agent with Masumi registry."""
        wrapper = bridge_adapter.wrap_agent(simple_agent)
        
        with patch('core.shared.masumi.bridge_adapter.MasumiRegistryClient') as mock_registry:
            mock_client_instance = AsyncMock()
            mock_client_instance.register_agent.return_value = True
            mock_registry.return_value.__aenter__.return_value = mock_client_instance
            
            result = await bridge_adapter.register_agent_with_masumi(
                wrapper=wrapper,
                api_endpoint="https://test.com/api",
                description="Test agent"
            )
            
            assert result == True
            mock_client_instance.register_agent.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_discover_masumi_agents(self, bridge_adapter):
        """Test discovering agents in Masumi network."""
        with patch('core.shared.masumi.bridge_adapter.MasumiRegistryClient') as mock_registry:
            mock_client_instance = AsyncMock()
            mock_client_instance.discover_agents.return_value = [
                {"name": "Agent1", "framework": "Agent Forge"},
                {"name": "Agent2", "framework": "Agent Forge"}
            ]
            mock_registry.return_value.__aenter__.return_value = mock_client_instance
            
            result = await bridge_adapter.discover_masumi_agents(
                capabilities=["web_navigation"],
                framework="Agent Forge"
            )
            
            assert len(result) == 2
            assert result[0]["name"] == "Agent1"
            mock_client_instance.discover_agents.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check(self, bridge_adapter):
        """Test health check of Masumi services."""
        with patch('core.shared.masumi.bridge_adapter.MasumiPaymentClient') as mock_payment:
            mock_client_instance = AsyncMock()
            mock_client_instance.health_check.return_value = True
            mock_payment.return_value.__aenter__.return_value = mock_client_instance
            
            health = await bridge_adapter.health_check()
            
            assert health["payment_service"] == True
            assert health["registry_service"] == True


class TestEndToEndIntegration:
    """End-to-end integration tests."""
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """Test complete Agent Forge + Masumi workflow."""
        # Initialize components
        config = MasumiConfig.for_testing()
        bridge = MasumiBridgeAdapter(config)
        agent = SimpleNavigationAgent(url="https://httpbin.org/html")
        
        # Wrap agent for Masumi
        wrapper = bridge.wrap_agent(
            agent=agent,
            agent_did="did:cardano:e2e_test",
            price_ada=2.5
        )
        
        # Mock external services
        with patch('core.shared.masumi.bridge_adapter.MasumiPaymentClient') as mock_payment, \
             patch('core.shared.masumi.bridge_adapter.MasumiRegistryClient') as mock_registry:
            
            # Mock payment client
            mock_payment_instance = AsyncMock()
            mock_payment_instance.verify_payment.return_value = True
            mock_payment_instance.claim_payment.return_value = "tx_123"
            mock_payment.return_value.__aenter__.return_value = mock_payment_instance
            
            # Mock registry client
            mock_registry_instance = AsyncMock()
            mock_registry_instance.register_agent.return_value = True
            mock_registry.return_value.__aenter__.return_value = mock_registry_instance
            
            # Mock agent execution
            with patch.object(agent, 'run') as mock_run:
                mock_run.return_value = {"title": "Test Page", "success": True}
                
                # Execute workflow
                result = await wrapper.execute_with_masumi(
                    job_id="e2e_test_job",
                    payment_proof="test_payment_proof",
                    requester_did="did:cardano:e2e_requester",
                    url="https://httpbin.org/html"
                )
                
                # Validate results
                assert result["job_id"] == "e2e_test_job"
                assert result["agent_did"] == "did:cardano:e2e_test"
                assert result["payment_verified"] == True
                assert result["payment_claimed"] == True
                assert "proof_hash" in result
                assert result["execution_time"] > 0
                
                # Register agent with Masumi
                registration_success = await bridge.register_agent_with_masumi(
                    wrapper=wrapper,
                    api_endpoint="https://e2e-test.com/api",
                    description="E2E test agent"
                )
                
                assert registration_success == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
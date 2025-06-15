"""
Unit tests for Othentic AVS integration.

Tests the core functionality of the Othentic Actively Validated Services
integration including agent registry, payment processing, and reputation validation.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, AsyncMock, patch
import aiohttp

from core.blockchain.othentic.client import OthenticAVSClient, OthenticConfig, AVSOperatorInfo
from core.blockchain.othentic.avs.agent_registry import (
    AgentRegistryAVS, AgentRegistration, AgentStatus, AgentCapability, AgentSearchQuery
)
from core.blockchain.othentic.avs.payment_processor import (
    UniversalPaymentAVS, PaymentRequest, PaymentTransaction, PaymentMethod, PaymentStatus,
    EscrowContract, EscrowStatus
)
from core.blockchain.othentic.avs.reputation import (
    ReputationValidationAVS, ReputationScore, ReputationTier, ReputationAction,
    ValidationRequest, ValidationVote, ValidationVoteRecord
)


class TestOthenticAVSClient:
    """Test cases for OthenticAVSClient."""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock Othentic configuration."""
        return OthenticConfig(
            api_key="test_api_key",
            agent_id="test_agent_123",
            base_url="https://test.othentic.xyz"
        )
    
    @pytest.fixture
    def mock_session(self):
        """Create mock aiohttp session."""
        session = AsyncMock()
        session.get = AsyncMock()
        session.post = AsyncMock()
        session.patch = AsyncMock()
        session.delete = AsyncMock()
        session.close = AsyncMock()
        return session
    
    @pytest.mark.asyncio
    async def test_client_initialization(self, mock_config):
        """Test client initialization with config."""
        client = OthenticAVSClient(mock_config)
        
        assert client.config == mock_config
        assert client.session is None
        assert hasattr(client, 'agent_registry')
        assert hasattr(client, 'payment_processor')
        assert hasattr(client, 'reputation')
        assert hasattr(client, 'compliance')
        assert hasattr(client, 'cross_chain')
    
    @pytest.mark.asyncio
    async def test_client_context_manager(self, mock_config):
        """Test client async context manager."""
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            client = OthenticAVSClient(mock_config)
            
            # Mock AVS initialization
            with patch.object(client, '_initialize_avs_services', new_callable=AsyncMock):
                async with client as active_client:
                    assert active_client.session is not None
                    assert active_client == client
                
                # Verify session is closed after context
                mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_register_as_operator(self, mock_config, mock_session):
        """Test operator registration."""
        client = OthenticAVSClient(mock_config)
        client.session = mock_session
        
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.raise_for_status = Mock()
        mock_response.json = AsyncMock(return_value={
            "operator_id": "test_agent_123",
            "status": "registered",
            "stake_amount": 32.0
        })
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        result = await client.register_as_operator(
            stake_amount=32.0,
            supported_chains=["ethereum", "polygon"]
        )
        
        assert result["operator_id"] == "test_agent_123"
        assert result["status"] == "registered"
        mock_session.post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_operator_status(self, mock_config, mock_session):
        """Test getting operator status."""
        client = OthenticAVSClient(mock_config)
        client.session = mock_session
        
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.raise_for_status = Mock()
        mock_response.json = AsyncMock(return_value={
            "operator_id": "test_agent_123",
            "stake_amount": 32.0,
            "reputation_score": 0.85,
            "validation_count": 100,
            "slash_count": 0,
            "is_active": True,
            "supported_chains": ["ethereum", "polygon"],
            "last_activity": "2024-01-01T00:00:00Z"
        })
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        status = await client.get_operator_status()
        
        assert isinstance(status, AVSOperatorInfo)
        assert status.operator_id == "test_agent_123"
        assert status.stake_amount == 32.0
        assert status.reputation_score == 0.85
        assert status.is_active is True


class TestAgentRegistryAVS:
    """Test cases for AgentRegistryAVS."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock Othentic client."""
        client = Mock()
        client.session = AsyncMock()
        client.config = Mock()
        client.config.base_url = "https://test.othentic.xyz"
        client.config.agent_id = "test_agent_123"
        return client
    
    @pytest.fixture
    def agent_registry(self, mock_client):
        """Create AgentRegistryAVS instance."""
        return AgentRegistryAVS(mock_client)
    
    @pytest.fixture
    def sample_registration(self):
        """Create sample agent registration."""
        return AgentRegistration(
            agent_id="test_agent_123",
            owner_address="0x123...",
            name="Test Agent",
            description="A test agent for unit testing",
            capabilities=[AgentCapability.WEB_SCRAPING, AgentCapability.DATA_EXTRACTION],
            supported_chains=["ethereum", "polygon"],
            stake_amount=Decimal("10.0"),
            reputation_score=0.75,
            registration_time=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            status=AgentStatus.ACTIVE
        )
    
    @pytest.mark.asyncio
    async def test_register_agent(self, agent_registry, mock_client, sample_registration):
        """Test agent registration."""
        agent_registry._initialized = True
        
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.raise_for_status = Mock()
        mock_response.json = AsyncMock(return_value={
            "agent_id": "test_agent_123",
            "status": "registered",
            "transaction_id": "0xabc123..."
        })
        mock_client.session.post.return_value.__aenter__.return_value = mock_response
        
        result = await agent_registry.register_agent(sample_registration)
        
        assert result["agent_id"] == "test_agent_123"
        assert result["status"] == "registered"
        mock_client.session.post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_agents(self, agent_registry, mock_client):
        """Test agent search functionality."""
        agent_registry._initialized = True
        
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.raise_for_status = Mock()
        mock_response.json = AsyncMock(return_value={
            "agents": [{
                "agent_id": "test_agent_123",
                "owner_address": "0x123...",
                "name": "Test Agent",
                "description": "A test agent",
                "capabilities": ["web_scraping", "data_extraction"],
                "supported_chains": ["ethereum"],
                "stake_amount": "10.0",
                "reputation_score": 0.75,
                "registration_time": "2024-01-01T00:00:00Z",
                "last_activity": "2024-01-01T00:00:00Z",
                "status": "active"
            }]
        })
        mock_client.session.get.return_value.__aenter__.return_value = mock_response
        
        query = AgentSearchQuery(
            capabilities=[AgentCapability.WEB_SCRAPING],
            min_reputation=0.5
        )
        
        agents = await agent_registry.search_agents(query)
        
        assert len(agents) == 1
        assert agents[0].agent_id == "test_agent_123"
        assert AgentCapability.WEB_SCRAPING in agents[0].capabilities


class TestUniversalPaymentAVS:
    """Test cases for UniversalPaymentAVS."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock Othentic client."""
        client = Mock()
        client.session = AsyncMock()
        client.config = Mock()
        client.config.base_url = "https://test.othentic.xyz"
        client.config.agent_id = "test_agent_123"
        return client
    
    @pytest.fixture
    def payment_processor(self, mock_client):
        """Create UniversalPaymentAVS instance."""
        processor = UniversalPaymentAVS(mock_client)
        processor._initialized = True
        processor._supported_methods = [PaymentMethod.ETHEREUM, PaymentMethod.USDC, PaymentMethod.STRIPE]
        return processor
    
    @pytest.fixture
    def sample_payment_request(self):
        """Create sample payment request."""
        return PaymentRequest(
            request_id="pay_123",
            payer_id="agent_456",
            payee_id="agent_789",
            amount=Decimal("100.0"),
            currency="USD",
            payment_method=PaymentMethod.USDC,
            description="Test payment for agent services"
        )
    
    @pytest.mark.asyncio
    async def test_create_payment_request(self, payment_processor, mock_client, sample_payment_request):
        """Test payment request creation."""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.raise_for_status = Mock()
        mock_response.json = AsyncMock(return_value={
            "request_id": "pay_123",
            "status": "created",
            "payment_url": "https://pay.othentic.xyz/pay_123"
        })
        mock_client.session.post.return_value.__aenter__.return_value = mock_response
        
        result = await payment_processor.create_payment_request(sample_payment_request)
        
        assert result["request_id"] == "pay_123"
        assert result["status"] == "created"
        mock_client.session.post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_payment(self, payment_processor, mock_client):
        """Test payment processing."""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.raise_for_status = Mock()
        mock_response.json = AsyncMock(return_value={
            "transaction_id": "tx_123",
            "request_id": "pay_123",
            "payer_id": "agent_456",
            "payee_id": "agent_789",
            "amount": "100.0",
            "currency": "USD",
            "payment_method": "usdc",
            "status": "completed",
            "escrow_status": "funded",
            "created_at": "2024-01-01T00:00:00Z"
        })
        mock_client.session.post.return_value.__aenter__.return_value = mock_response
        
        transaction = await payment_processor.process_payment("pay_123")
        
        assert isinstance(transaction, PaymentTransaction)
        assert transaction.transaction_id == "tx_123"
        assert transaction.status == PaymentStatus.COMPLETED
        assert transaction.payment_method == PaymentMethod.USDC
    
    @pytest.mark.asyncio
    async def test_create_escrow(self, payment_processor, mock_client, sample_payment_request):
        """Test escrow contract creation."""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.raise_for_status = Mock()
        mock_response.json = AsyncMock(return_value={
            "escrow_id": "escrow_123",
            "payer_id": "agent_456",
            "payee_id": "agent_789",
            "amount": "100.0",
            "currency": "USD",
            "status": "created",
            "release_conditions": ["task_completion"],
            "timeout_timestamp": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
            "created_at": datetime.utcnow().isoformat()
        })
        mock_client.session.post.return_value.__aenter__.return_value = mock_response
        
        escrow = await payment_processor.create_escrow(
            sample_payment_request,
            ["task_completion"]
        )
        
        assert isinstance(escrow, EscrowContract)
        assert escrow.escrow_id == "escrow_123"
        assert escrow.status == EscrowStatus.CREATED
        assert "task_completion" in escrow.release_conditions


class TestReputationValidationAVS:
    """Test cases for ReputationValidationAVS."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock Othentic client."""
        client = Mock()
        client.session = AsyncMock()
        client.config = Mock()
        client.config.base_url = "https://test.othentic.xyz"
        client.config.agent_id = "test_agent_123"
        return client
    
    @pytest.fixture
    def reputation_avs(self, mock_client):
        """Create ReputationValidationAVS instance."""
        avs = ReputationValidationAVS(mock_client)
        avs._initialized = True
        return avs
    
    @pytest.mark.asyncio
    async def test_get_reputation_score(self, reputation_avs, mock_client):
        """Test getting reputation score."""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.raise_for_status = Mock()
        mock_response.json = AsyncMock(return_value={
            "agent_id": "test_agent_123",
            "overall_score": "0.85",
            "tier": "expert",
            "task_completion_rate": "0.95",
            "fraud_reports": 0,
            "stake_amount": "32.0",
            "validation_accuracy": "0.90",
            "peer_review_score": "0.80",
            "last_updated": "2024-01-01T00:00:00Z",
            "score_history": []
        })
        mock_client.session.get.return_value.__aenter__.return_value = mock_response
        
        score = await reputation_avs.get_reputation_score("test_agent_123")
        
        assert isinstance(score, ReputationScore)
        assert score.agent_id == "test_agent_123"
        assert score.overall_score == Decimal("0.85")
        assert score.tier == ReputationTier.EXPERT
    
    @pytest.mark.asyncio
    async def test_create_validation_request(self, reputation_avs, mock_client):
        """Test creating validation request."""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.raise_for_status = Mock()
        mock_response.json = AsyncMock(return_value={
            "request_id": "val_123",
            "status": "pending"
        })
        mock_client.session.post.return_value.__aenter__.return_value = mock_response
        
        request = await reputation_avs.create_validation_request(
            agent_id="test_agent_123",
            action=ReputationAction.TASK_COMPLETION,
            evidence={"task_id": "task_456", "completion_proof": "0xabc123..."},
            stake_requirement=Decimal("1.0")
        )
        
        assert isinstance(request, ValidationRequest)
        assert request.agent_id == "test_agent_123"
        assert request.action == ReputationAction.TASK_COMPLETION
    
    @pytest.mark.asyncio
    async def test_vote_on_validation(self, reputation_avs, mock_client):
        """Test voting on validation request."""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.raise_for_status = Mock()
        mock_response.json = AsyncMock(return_value={
            "vote_id": "vote_123"
        })
        mock_client.session.post.return_value.__aenter__.return_value = mock_response
        
        vote_record = await reputation_avs.vote_on_validation(
            request_id="val_123",
            vote=ValidationVote.APPROVE,
            stake_amount=Decimal("5.0"),
            justification="Task completed successfully with high quality"
        )
        
        assert isinstance(vote_record, ValidationVoteRecord)
        assert vote_record.vote == ValidationVote.APPROVE
        assert vote_record.stake_weight == Decimal("5.0")


class TestIntegrationScenarios:
    """Integration test scenarios combining multiple AVS services."""
    
    @pytest.mark.asyncio
    async def test_agent_lifecycle_scenario(self):
        """Test complete agent lifecycle with Othentic integration."""
        # This would be an integration test that:
        # 1. Registers an agent
        # 2. Creates payment requests
        # 3. Processes payments through escrow
        # 4. Updates reputation based on task completion
        # 5. Validates reputation changes
        
        config = OthenticConfig(
            api_key="test_key",
            agent_id="test_agent",
            base_url="https://test.othentic.xyz"
        )
        
        # Mock the entire flow
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            # Mock various API responses for the lifecycle
            mock_responses = [
                # Agent registration
                {"agent_id": "test_agent", "status": "registered"},
                # Payment creation
                {"request_id": "pay_123", "status": "created"},
                # Payment processing
                {"transaction_id": "tx_123", "status": "completed"},
                # Reputation update
                {"score_change": "+0.05", "new_score": "0.80"}
            ]
            
            mock_response = AsyncMock()
            mock_response.raise_for_status = Mock()
            mock_response.json = AsyncMock(side_effect=mock_responses)
            mock_session.get.return_value.__aenter__.return_value = mock_response
            mock_session.post.return_value.__aenter__.return_value = mock_response
            
            client = OthenticAVSClient(config)
            
            with patch.object(client, '_initialize_avs_services', new_callable=AsyncMock):
                async with client:
                    # Test that all services are available
                    assert client.agent_registry is not None
                    assert client.payment_processor is not None
                    assert client.reputation is not None
                    assert client.compliance is not None
                    assert client.cross_chain is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
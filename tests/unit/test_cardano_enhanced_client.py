"""
Unit tests for Enhanced Cardano Client

Tests the core functionality of the EnhancedCardanoClient including:
- Agent registry operations
- Service marketplace functions
- Revenue sharing mechanisms
- Cross-chain integration
- Compliance features
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
import json

# Import classes to test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from core.blockchain.cardano_enhanced_client import (
    EnhancedCardanoClient,
    AgentProfile,
    ServiceRequest,
    RevenueShare
)
from core.blockchain.nmkr_integration import ExecutionProof


class TestAgentProfile:
    """Test AgentProfile dataclass functionality."""
    
    def test_agent_profile_creation(self):
        """Test creating agent profile with required fields."""
        profile = AgentProfile(
            owner_address="addr1_test_owner",
            agent_id="test_agent_001",
            metadata_uri="ipfs://QmTestMetadata",
            staked_amount=500.0,
            reputation_score=0.85,
            capabilities=["web_automation", "ai_analysis"],
            total_executions=100,
            successful_executions=95
        )
        
        assert profile.owner_address == "addr1_test_owner"
        assert profile.agent_id == "test_agent_001"
        assert profile.staked_amount == 500.0
        assert profile.reputation_score == 0.85
        assert len(profile.capabilities) == 2
        assert profile.framework_version == "1.0.0"
        assert profile.created_at  # Should be auto-generated
    
    def test_agent_profile_with_custom_timestamp(self):
        """Test creating agent profile with custom timestamp."""
        custom_time = "2025-01-01T00:00:00"
        profile = AgentProfile(
            owner_address="addr1_test_owner",
            agent_id="test_agent_002",
            metadata_uri="ipfs://QmTestMetadata",
            staked_amount=1000.0,
            reputation_score=0.90,
            capabilities=["blockchain"],
            total_executions=50,
            successful_executions=50,
            created_at=custom_time
        )
        
        assert profile.created_at == custom_time


class TestServiceRequest:
    """Test ServiceRequest dataclass functionality."""
    
    def test_service_request_creation(self):
        """Test creating service request with required fields."""
        request = ServiceRequest(
            requester_address="addr1_test_requester",
            agent_id="test_agent_001",
            service_hash="test_service_hash_001",
            payment_amount=25.0,
            escrow_deadline="2025-12-31T23:59:59",
            task_description="Test web analysis task"
        )
        
        assert request.requester_address == "addr1_test_requester"
        assert request.agent_id == "test_agent_001"
        assert request.payment_amount == 25.0
        assert request.status == "pending"
        assert request.execution_proof is None
    
    def test_service_request_hash_generation(self):
        """Test deterministic hash generation for service requests."""
        request1 = ServiceRequest(
            requester_address="addr1_test_requester",
            agent_id="test_agent_001",
            service_hash="test_service_hash_001",
            payment_amount=25.0,
            escrow_deadline="2025-12-31T23:59:59",
            task_description="Test web analysis task"
        )
        
        request2 = ServiceRequest(
            requester_address="addr1_test_requester",
            agent_id="test_agent_001",
            service_hash="test_service_hash_001",
            payment_amount=25.0,
            escrow_deadline="2025-12-31T23:59:59",
            task_description="Test web analysis task"
        )
        
        # Same requests should generate same hash
        assert request1.generate_hash() == request2.generate_hash()
        
        # Different requests should generate different hashes
        request2.payment_amount = 50.0
        assert request1.generate_hash() != request2.generate_hash()


class TestRevenueShare:
    """Test RevenueShare dataclass functionality."""
    
    def test_revenue_share_creation(self):
        """Test creating revenue share with required fields."""
        share = RevenueShare(
            recipient_address="addr1_test_recipient",
            participation_tokens=1000,
            accumulated_rewards=0.0,
            last_claim_block=0,
            contribution_score=0.85
        )
        
        assert share.recipient_address == "addr1_test_recipient"
        assert share.participation_tokens == 1000
        assert share.accumulated_rewards == 0.0
        assert share.contribution_score == 0.85
    
    def test_calculate_rewards(self):
        """Test reward calculation based on participation tokens."""
        share = RevenueShare(
            recipient_address="addr1_test_recipient",
            participation_tokens=2000,
            accumulated_rewards=0.0,
            last_claim_block=0,
            contribution_score=0.85
        )
        
        # Test with total revenue and tokens
        total_revenue = 1000.0
        total_tokens = 10000
        
        expected_reward = (2000 / 10000) * 1000.0  # 200.0 ADA
        calculated_reward = share.calculate_rewards(total_revenue, total_tokens)
        
        assert calculated_reward == expected_reward
    
    def test_calculate_rewards_zero_tokens(self):
        """Test reward calculation with zero total tokens."""
        share = RevenueShare(
            recipient_address="addr1_test_recipient",
            participation_tokens=1000,
            accumulated_rewards=0.0,
            last_claim_block=0
        )
        
        # Should return 0 when total tokens is 0
        reward = share.calculate_rewards(1000.0, 0)
        assert reward == 0.0


class TestEnhancedCardanoClient:
    """Test EnhancedCardanoClient functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock Enhanced Cardano Client for testing."""
        with patch('core.blockchain.cardano_enhanced_client.NMKRClient') as mock_nmkr:
            mock_nmkr_instance = AsyncMock()
            mock_nmkr.return_value = mock_nmkr_instance
            
            client = EnhancedCardanoClient(
                nmkr_api_key="test_key",
                blockfrost_project_id="test_project",
                policy_id="test_policy"
            )
            client.nmkr_client = mock_nmkr_instance
            
            return client
    
    @pytest.fixture
    def sample_agent_profile(self):
        """Create sample agent profile for testing."""
        return AgentProfile(
            owner_address="addr1_test_owner",
            agent_id="test_agent_001",
            metadata_uri="ipfs://QmTestMetadata",
            staked_amount=500.0,
            reputation_score=0.85,
            capabilities=["web_automation", "ai_analysis"],
            total_executions=100,
            successful_executions=95
        )
    
    @pytest.fixture
    def sample_service_request(self):
        """Create sample service request for testing."""
        return ServiceRequest(
            requester_address="addr1_test_requester",
            agent_id="test_agent_001",
            service_hash="test_service_hash_001",
            payment_amount=25.0,
            escrow_deadline="2025-12-31T23:59:59",
            task_description="Test web analysis task"
        )
    
    def test_client_initialization(self):
        """Test Enhanced Cardano Client initialization."""
        client = EnhancedCardanoClient(
            nmkr_api_key="test_key",
            blockfrost_project_id="test_project",
            policy_id="test_policy"
        )
        
        assert client.blockfrost_project_id == "test_project"
        assert client.policy_id == "test_policy"
        assert isinstance(client.agent_registry, dict)
        assert isinstance(client.service_requests, dict)
        assert isinstance(client.revenue_shares, dict)
    
    def test_get_minimum_stake(self, mock_client):
        """Test minimum stake calculation based on capabilities."""
        # Test base stake
        base_capabilities = ["basic_task"]
        min_stake = mock_client._get_minimum_stake(base_capabilities)
        assert min_stake >= 100.0  # Base stake is 100 ADA
        
        # Test enhanced capabilities
        advanced_capabilities = ["blockchain", "smart_contracts", "ai_analysis"]
        advanced_stake = mock_client._get_minimum_stake(advanced_capabilities)
        assert advanced_stake > min_stake
        
        # Test specific capability multipliers
        blockchain_capabilities = ["blockchain"]
        blockchain_stake = mock_client._get_minimum_stake(blockchain_capabilities)
        assert blockchain_stake == 100.0 * (1.0 + 2.0)  # Base + blockchain multiplier
    
    def test_calculate_stake_tier(self, mock_client):
        """Test stake tier calculation."""
        assert mock_client._calculate_stake_tier(50.0) == "basic"
        assert mock_client._calculate_stake_tier(500.0) == "standard"
        assert mock_client._calculate_stake_tier(5000.0) == "professional"
        assert mock_client._calculate_stake_tier(15000.0) == "enterprise"
    
    @pytest.mark.asyncio
    async def test_register_agent_success(self, mock_client, sample_agent_profile):
        """Test successful agent registration."""
        # Mock successful NFT minting
        mock_client.nmkr_client.mint_nft.return_value = {
            "transaction_id": "tx_test_001",
            "status": "success"
        }
        
        stake_amount = 500.0
        result = await mock_client.register_agent(sample_agent_profile, stake_amount)
        
        assert result["status"] == "success"
        assert result["agent_id"] == sample_agent_profile.agent_id
        assert result["stake_amount"] == stake_amount
        assert "transaction_id" in result
        assert sample_agent_profile.agent_id in mock_client.agent_registry
    
    @pytest.mark.asyncio
    async def test_register_agent_insufficient_stake(self, mock_client, sample_agent_profile):
        """Test agent registration with insufficient stake."""
        insufficient_stake = 10.0  # Much lower than required
        result = await mock_client.register_agent(sample_agent_profile, insufficient_stake)
        
        assert result["status"] == "error"
        assert "Insufficient stake" in result["error"]
        assert "minimum_required" in result
    
    @pytest.mark.asyncio
    async def test_find_agents(self, mock_client, sample_agent_profile):
        """Test agent discovery functionality."""
        # Add agent to registry
        mock_client.agent_registry[sample_agent_profile.agent_id] = sample_agent_profile
        
        # Test finding agents by capabilities
        agents = await mock_client.find_agents(
            capabilities=["web_automation"],
            min_reputation=0.8,
            max_agents=5
        )
        
        assert len(agents) == 1
        assert agents[0]["agent_id"] == sample_agent_profile.agent_id
        assert agents[0]["reputation_score"] == sample_agent_profile.reputation_score
    
    @pytest.mark.asyncio
    async def test_find_agents_no_match(self, mock_client, sample_agent_profile):
        """Test agent discovery with no matching agents."""
        # Add agent to registry
        mock_client.agent_registry[sample_agent_profile.agent_id] = sample_agent_profile
        
        # Test finding agents with non-matching criteria
        agents = await mock_client.find_agents(
            capabilities=["nonexistent_capability"],
            min_reputation=0.5,
            max_agents=5
        )
        
        assert len(agents) == 0
    
    @pytest.mark.asyncio
    async def test_create_escrow_success(self, mock_client, sample_service_request):
        """Test successful escrow creation."""
        # Mock successful NFT minting
        mock_client.nmkr_client.mint_nft.return_value = {
            "transaction_id": "tx_escrow_001",
            "status": "success"
        }
        
        result = await mock_client.create_escrow(sample_service_request)
        
        assert result["status"] == "success"
        assert "escrow_id" in result
        assert result["payment_amount"] == sample_service_request.payment_amount
        assert "transaction_id" in result
        assert result["escrow_id"] in mock_client.service_requests
    
    @pytest.mark.asyncio
    async def test_release_escrow_success(self, mock_client, sample_service_request):
        """Test successful escrow release."""
        # Setup escrow
        escrow_id = sample_service_request.generate_hash()
        mock_client.service_requests[escrow_id] = sample_service_request
        
        # Create execution proof
        execution_proof = ExecutionProof(
            agent_id=sample_service_request.agent_id,
            execution_id="test_exec_001",
            timestamp=datetime.now().isoformat(),
            task_completed=True,
            execution_time=2.5,
            results={"test": "result"},
            metadata={"test": "metadata"}
        )
        
        result = await mock_client.release_escrow(escrow_id, execution_proof)
        
        assert result["status"] == "success"
        assert result["escrow_id"] == escrow_id
        assert result["payment_released"] == sample_service_request.payment_amount
        assert result["agent_id"] == sample_service_request.agent_id
    
    @pytest.mark.asyncio
    async def test_release_escrow_not_found(self, mock_client):
        """Test escrow release with non-existent escrow."""
        execution_proof = ExecutionProof(
            agent_id="test_agent",
            execution_id="test_exec_001",
            timestamp=datetime.now().isoformat(),
            task_completed=True,
            execution_time=2.5,
            results={"test": "result"},
            metadata={"test": "metadata"}
        )
        
        result = await mock_client.release_escrow("nonexistent_escrow", execution_proof)
        
        assert result["status"] == "error"
        assert "Escrow not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_distribute_revenue_success(self, mock_client):
        """Test successful revenue distribution."""
        # Setup revenue shares
        mock_client.revenue_shares["addr1_recipient_1"] = RevenueShare(
            recipient_address="addr1_recipient_1",
            participation_tokens=2000,
            accumulated_rewards=0.0,
            last_claim_block=0,
            contribution_score=0.9
        )
        
        mock_client.revenue_shares["addr1_recipient_2"] = RevenueShare(
            recipient_address="addr1_recipient_2",
            participation_tokens=3000,
            accumulated_rewards=0.0,
            last_claim_block=0,
            contribution_score=0.8
        )
        
        total_revenue = 1000.0
        result = await mock_client.distribute_revenue(total_revenue, "2025-Q1")
        
        assert result["status"] == "success"
        assert result["total_revenue"] == total_revenue
        assert result["total_recipients"] == 2
        assert len(result["distributions"]) == 2
        
        # Check distribution calculations
        total_tokens = 2000 + 3000  # 5000
        expected_reward_1 = (2000 / 5000) * 1000.0  # 400.0 ADA
        expected_reward_2 = (3000 / 5000) * 1000.0  # 600.0 ADA
        
        distributions = {d["recipient_address"]: d for d in result["distributions"]}
        assert distributions["addr1_recipient_1"]["reward_amount"] == expected_reward_1
        assert distributions["addr1_recipient_2"]["reward_amount"] == expected_reward_2
    
    @pytest.mark.asyncio
    async def test_distribute_revenue_no_participants(self, mock_client):
        """Test revenue distribution with no participants."""
        result = await mock_client.distribute_revenue(1000.0, "2025-Q1")
        
        assert result["status"] == "error"
        assert "No revenue share participants" in result["error"]
    
    @pytest.mark.asyncio
    async def test_claim_rewards_success(self, mock_client):
        """Test successful reward claiming."""
        # Setup revenue share with accumulated rewards
        recipient_address = "addr1_recipient_test"
        mock_client.revenue_shares[recipient_address] = RevenueShare(
            recipient_address=recipient_address,
            participation_tokens=1000,
            accumulated_rewards=250.0,
            last_claim_block=0,
            contribution_score=0.85
        )
        
        # Mock successful NFT minting
        mock_client.nmkr_client.mint_nft.return_value = {
            "transaction_id": "tx_reward_claim_001",
            "status": "success"
        }
        
        result = await mock_client.claim_rewards(recipient_address)
        
        assert result["status"] == "success"
        assert result["recipient_address"] == recipient_address
        assert result["claimed_amount"] == 250.0
        assert "transaction_id" in result
        
        # Check that accumulated rewards are reset
        assert mock_client.revenue_shares[recipient_address].accumulated_rewards == 0.0
    
    @pytest.mark.asyncio
    async def test_claim_rewards_no_rewards(self, mock_client):
        """Test reward claiming with no accumulated rewards."""
        recipient_address = "addr1_recipient_test"
        mock_client.revenue_shares[recipient_address] = RevenueShare(
            recipient_address=recipient_address,
            participation_tokens=1000,
            accumulated_rewards=0.0,
            last_claim_block=0
        )
        
        result = await mock_client.claim_rewards(recipient_address)
        
        assert result["status"] == "error"
        assert "No rewards available" in result["error"]
    
    @pytest.mark.asyncio
    async def test_claim_rewards_not_found(self, mock_client):
        """Test reward claiming for non-existent recipient."""
        result = await mock_client.claim_rewards("addr1_nonexistent")
        
        assert result["status"] == "error"
        assert "No revenue share found" in result["error"]
    
    def test_verify_execution_proof_valid(self, mock_client, sample_service_request):
        """Test execution proof verification with valid proof."""
        execution_proof = ExecutionProof(
            agent_id=sample_service_request.agent_id,
            execution_id="test_exec_001",
            timestamp=datetime.now().isoformat(),
            task_completed=True,
            execution_time=2.5,
            results={"test": "result"},
            metadata={"test": "metadata"}
        )
        
        is_valid = mock_client._verify_execution_proof(execution_proof, sample_service_request)
        assert is_valid is True
    
    def test_verify_execution_proof_invalid_agent(self, mock_client, sample_service_request):
        """Test execution proof verification with wrong agent ID."""
        execution_proof = ExecutionProof(
            agent_id="wrong_agent_id",
            execution_id="test_exec_001",
            timestamp=datetime.now().isoformat(),
            task_completed=True,
            execution_time=2.5,
            results={"test": "result"},
            metadata={"test": "metadata"}
        )
        
        is_valid = mock_client._verify_execution_proof(execution_proof, sample_service_request)
        assert is_valid is False
    
    def test_verify_execution_proof_task_not_completed(self, mock_client, sample_service_request):
        """Test execution proof verification with incomplete task."""
        execution_proof = ExecutionProof(
            agent_id=sample_service_request.agent_id,
            execution_id="test_exec_001",
            timestamp=datetime.now().isoformat(),
            task_completed=False,
            execution_time=2.5,
            results={"test": "result"},
            metadata={"test": "metadata"}
        )
        
        is_valid = mock_client._verify_execution_proof(execution_proof, sample_service_request)
        assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_register_cross_chain_service_success(self, mock_client, sample_agent_profile):
        """Test successful cross-chain service registration."""
        # Add agent to registry
        mock_client.agent_registry[sample_agent_profile.agent_id] = sample_agent_profile
        
        # Mock successful NFT minting
        mock_client.nmkr_client.mint_nft.return_value = {
            "transaction_id": "tx_cross_chain_001",
            "status": "success"
        }
        
        supported_chains = ["cardano", "ethereum", "polygon"]
        result = await mock_client.register_cross_chain_service(
            sample_agent_profile.agent_id,
            supported_chains
        )
        
        assert result["status"] == "success"
        assert result["agent_id"] == sample_agent_profile.agent_id
        assert result["supported_chains"] == supported_chains
        assert "transaction_id" in result
    
    @pytest.mark.asyncio
    async def test_register_cross_chain_service_agent_not_found(self, mock_client):
        """Test cross-chain registration with non-existent agent."""
        result = await mock_client.register_cross_chain_service(
            "nonexistent_agent",
            ["cardano", "ethereum"]
        )
        
        assert result["status"] == "error"
        assert "Agent not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_update_agent_reputation(self, mock_client, sample_agent_profile):
        """Test agent reputation update functionality."""
        # Add agent to registry
        original_reputation = sample_agent_profile.reputation_score
        original_executions = sample_agent_profile.total_executions
        original_successful = sample_agent_profile.successful_executions
        
        mock_client.agent_registry[sample_agent_profile.agent_id] = sample_agent_profile
        
        # Update reputation with successful execution
        await mock_client._update_agent_reputation(
            sample_agent_profile.agent_id,
            success=True,
            execution_time=5.0
        )
        
        updated_profile = mock_client.agent_registry[sample_agent_profile.agent_id]
        assert updated_profile.total_executions == original_executions + 1
        assert updated_profile.successful_executions == original_successful + 1
        # Reputation should be at least the original (may increase)
        assert updated_profile.reputation_score >= original_reputation
    
    def test_get_current_block_height(self, mock_client):
        """Test current block height calculation."""
        # Should return a positive integer
        block_height = mock_client._get_current_block_height()
        assert isinstance(block_height, int)
        assert block_height > 0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
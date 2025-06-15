"""
Integration tests for Cardano Enhanced Agent

Tests the full integration of the CardanoEnhancedAgent including:
- Complete agent lifecycle operations
- Real blockchain integration flows
- Multi-component interaction testing
- Agent framework integration
- MCP server compatibility
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
import json
import tempfile
import os

# Import classes to test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from examples.cardano_enhanced_agent import CardanoEnhancedAgent
from core.blockchain.cardano_enhanced_client import (
    EnhancedCardanoClient,
    AgentProfile,
    ServiceRequest,
    RevenueShare
)
from core.blockchain.nmkr_integration import ExecutionProof


class TestCardanoEnhancedAgentIntegration:
    """Integration tests for Cardano Enhanced Agent."""
    
    @pytest.fixture
    def agent_config(self):
        """Create test configuration for agent."""
        return {
            "agent_id": "test_cardano_enhanced_agent",
            "owner_address": "addr1_test_owner_integration",
            "nmkr_api_key": "test_integration_key",
            "blockfrost_project_id": "test_integration_project"
        }
    
    @pytest.fixture
    async def mock_agent(self, agent_config):
        """Create mock Cardano Enhanced Agent for testing."""
        with patch('examples.cardano_enhanced_agent.EnhancedCardanoClient') as mock_client_class:
            # Setup mock client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)
            
            # Create agent
            agent = CardanoEnhancedAgent(name="test_cardano_enhanced", config=agent_config)
            
            # Mock the browser client
            agent.browser_client = AsyncMock()
            agent.browser_client.navigate.return_value = {
                "page_title": "Test Page",
                "content": "Test page content with blockchain and cardano keywords",
                "status": "success"
            }
            
            yield agent, mock_client
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent_config):
        """Test agent initialization with configuration."""
        agent = CardanoEnhancedAgent(name="test_init", config=agent_config)
        
        assert agent.agent_id == agent_config["agent_id"]
        assert agent.owner_address == agent_config["owner_address"]
        assert agent.nmkr_api_key == agent_config["nmkr_api_key"]
        assert agent.blockfrost_project_id == agent_config["blockfrost_project_id"]
        
        # Check capabilities
        assert "web_automation" in agent.capabilities
        assert "blockchain" in agent.capabilities
        assert "smart_contracts" in agent.capabilities
        
        # Check pricing
        assert agent.service_pricing["web_analysis"] == 25.0
        assert agent.service_pricing["blockchain_audit"] == 100.0
    
    @pytest.mark.asyncio
    async def test_full_demo_operation(self, mock_agent):
        """Test complete full demo operation."""
        agent, mock_client = mock_agent
        
        # Mock all client operations
        mock_client.register_agent.return_value = {
            "status": "success",
            "agent_id": agent.agent_id,
            "transaction_id": "tx_register_001",
            "stake_tier": "professional",
            "capabilities": agent.capabilities
        }
        
        mock_client.find_agents.return_value = [
            {
                "agent_id": agent.agent_id,
                "reputation_score": 0.85,
                "capabilities": ["web_automation", "ai_analysis"]
            }
        ]
        
        mock_client.create_escrow.return_value = {
            "status": "success",
            "escrow_id": "escrow_test_001",
            "transaction_id": "tx_escrow_001",
            "payment_amount": 25.0
        }
        
        mock_client.release_escrow.return_value = {
            "status": "success",
            "escrow_id": "escrow_test_001",
            "payment_released": 25.0,
            "agent_id": agent.agent_id,
            "reputation_updated": True
        }
        
        mock_client.distribute_revenue.return_value = {
            "status": "success",
            "total_revenue": 5000.0,
            "total_recipients": 3,
            "distributions": [
                {"recipient_address": "addr1_dev", "reward_amount": 2500.0},
                {"recipient_address": "addr1_validator", "reward_amount": 1500.0},
                {"recipient_address": "addr1_support", "reward_amount": 1000.0}
            ]
        }
        
        mock_client.claim_rewards.return_value = {
            "status": "success",
            "recipient_address": "addr1_dev",
            "claimed_amount": 250.0,
            "transaction_id": "tx_claim_001"
        }
        
        mock_client.register_cross_chain_service.return_value = {
            "status": "success",
            "agent_id": agent.agent_id,
            "supported_chains": ["cardano", "ethereum", "polygon", "solana", "avalanche"],
            "transaction_id": "tx_cross_chain_001"
        }
        
        # Run full demo
        result = await agent.run("full_demo")
        
        # Verify results
        assert result is not None
        assert result["demo_type"] == "full_cardano_ai_economy"
        assert result["agent_id"] == agent.agent_id
        assert "phases" in result
        assert "summary" in result
        
        # Check all phases completed
        phases = result["phases"]
        assert "agent_registration" in phases
        assert "service_marketplace" in phases
        assert "governance_economics" in phases
        assert "cross_chain_integration" in phases
        assert "compliance_framework" in phases
        
        # Verify summary metrics
        summary = result["summary"]
        assert summary["total_phases"] == 5
        assert "key_innovations" in summary
        assert "technical_achievements" in summary
    
    @pytest.mark.asyncio
    async def test_register_operation(self, mock_agent):
        """Test agent registration operation."""
        agent, mock_client = mock_agent
        
        # Mock registration
        mock_client.register_agent.return_value = {
            "status": "success",
            "agent_id": agent.agent_id,
            "transaction_id": "tx_register_test",
            "stake_tier": "professional",
            "capabilities": agent.capabilities,
            "stake_amount": 1000.0
        }
        
        # Test registration
        result = await agent.run("register", stake_amount=1000.0)
        
        assert result is not None
        assert result["operation"] == "agent_registration"
        assert result["agent_id"] == agent.agent_id
        
        registration_result = result["registration_result"]
        assert registration_result["status"] == "success"
        assert registration_result["stake_amount"] == 1000.0
        assert registration_result["stake_tier"] == "professional"
        
        # Verify stake details
        stake_details = result["stake_details"]
        assert stake_details["amount"] == 1000.0
        assert stake_details["tier"] == "professional"
        assert stake_details["capabilities"] == agent.capabilities
    
    @pytest.mark.asyncio
    async def test_marketplace_operation(self, mock_agent):
        """Test marketplace demonstration operation."""
        agent, mock_client = mock_agent
        
        # Mock marketplace operations
        mock_client.find_agents.return_value = [
            {
                "agent_id": "agent_001",
                "reputation_score": 0.9,
                "capabilities": ["web_automation", "ai_analysis"]
            },
            {
                "agent_id": "agent_002", 
                "reputation_score": 0.85,
                "capabilities": ["web_automation"]
            }
        ]
        
        mock_client.create_escrow.return_value = {
            "status": "success",
            "escrow_id": "marketplace_escrow_001",
            "transaction_id": "tx_marketplace_escrow",
            "payment_amount": 25.0,
            "deadline": (datetime.now() + timedelta(hours=24)).isoformat()
        }
        
        mock_client.release_escrow.return_value = {
            "status": "success",
            "escrow_id": "marketplace_escrow_001",
            "payment_released": 25.0,
            "agent_id": agent.agent_id,
            "execution_proof_hash": "proof_hash_123",
            "reputation_updated": True
        }
        
        # Test marketplace operation
        result = await agent.run("marketplace")
        
        assert result is not None
        assert result["operation"] == "service_marketplace"
        assert "components" in result
        
        components = result["components"]
        
        # Check service discovery
        assert "service_discovery" in components
        discovery = components["service_discovery"]
        assert discovery["agents_found"] == 2
        assert len(discovery["results"]) == 2
        
        # Check escrow creation
        assert "escrow_creation" in components
        escrow_creation = components["escrow_creation"]
        assert escrow_creation["escrow_result"]["status"] == "success"
        assert escrow_creation["service_request"]["payment_amount"] == 25.0
        
        # Check escrow release
        assert "escrow_release" in components
        escrow_release = components["escrow_release"]
        assert escrow_release["release_result"]["status"] == "success"
        assert escrow_release["release_result"]["payment_released"] == 25.0
    
    @pytest.mark.asyncio
    async def test_governance_operation(self, mock_agent):
        """Test governance demonstration operation."""
        agent, mock_client = mock_agent
        
        # Mock governance operations
        mock_client.distribute_revenue.return_value = {
            "status": "success",
            "total_revenue": 5000.0,
            "total_recipients": 3,
            "distribution_period": "2025-Q1",
            "distributions": [
                {
                    "recipient_address": "addr1_community_dev_001",
                    "participation_tokens": 2500,
                    "reward_amount": 2500.0,
                    "contribution_score": 0.95
                },
                {
                    "recipient_address": "addr1_community_validator_002",
                    "participation_tokens": 1500,
                    "reward_amount": 1500.0,
                    "contribution_score": 0.88
                },
                {
                    "recipient_address": "addr1_community_support_003",
                    "participation_tokens": 1000,
                    "reward_amount": 1000.0,
                    "contribution_score": 0.82
                }
            ]
        }
        
        mock_client.claim_rewards.return_value = {
            "status": "success",
            "recipient_address": "addr1_community_dev_001",
            "claimed_amount": 250.0,
            "transaction_id": "tx_claim_governance"
        }
        
        # Test governance operation
        result = await agent.run("governance")
        
        assert result is not None
        assert result["operation"] == "governance_economics"
        assert "components" in result
        
        components = result["components"]
        
        # Check participation setup
        assert "participation_setup" in components
        participation = components["participation_setup"]
        assert participation["total_participants"] == 3
        assert participation["total_tokens"] == 5000  # 2500 + 1500 + 1000
        
        # Check revenue distribution
        assert "revenue_distribution" in components
        distribution = components["revenue_distribution"]
        assert distribution["total_revenue"] == 5000.0
        assert distribution["distribution_result"]["status"] == "success"
        
        # Check reward claims
        assert "reward_claims" in components
        claims = components["reward_claims"]
        assert claims["claims_processed"] == 2  # First 2 participants
    
    @pytest.mark.asyncio
    async def test_compliance_operation(self, mock_agent):
        """Test compliance demonstration operation."""
        agent, mock_client = mock_agent
        
        # Test compliance operation
        result = await agent.run("compliance")
        
        assert result is not None
        assert result["operation"] == "enterprise_compliance_framework"
        assert "components" in result
        
        components = result["components"]
        
        # Check KYC/AML framework
        assert "kyc_aml_framework" in components
        kyc_framework = components["kyc_aml_framework"]
        assert kyc_framework["compliance_standard"] == "REGKYC - Privacy-Preserving ABAC"
        assert "features" in kyc_framework
        assert "implementation" in kyc_framework
        
        # Check GDPR compliance
        assert "gdpr_compliance" in components
        gdpr = components["gdpr_compliance"]
        assert gdpr["compliance_standard"] == "GDPR for Blockchain Systems"
        assert "data_protection_measures" in gdpr
        assert "technical_safeguards" in gdpr
        
        # Check security standards
        assert "security_standards" in components
        security = components["security_standards"]
        assert "access_control" in security
        assert "audit_mechanisms" in security
        assert "risk_management" in security
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_agent):
        """Test error handling in agent operations."""
        agent, mock_client = mock_agent
        
        # Mock client to raise exception
        mock_client.register_agent.side_effect = Exception("Test error")
        
        # Test error handling
        result = await agent.run("register")
        
        assert result is not None
        assert result["status"] == "error"
        assert "Test error" in result["error"]
        assert result["operation"] == "register"
        assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_service_execution_simulation(self, mock_agent):
        """Test service execution simulation."""
        agent, mock_client = mock_agent
        
        # Create service request
        service_request = ServiceRequest(
            requester_address="addr1_test_requester",
            agent_id=agent.agent_id,
            service_hash="test_service_simulation",
            payment_amount=50.0,
            escrow_deadline=(datetime.now() + timedelta(hours=12)).isoformat(),
            task_description="Test competitor analysis simulation"
        )
        
        # Test service execution simulation
        execution_proof = await agent._simulate_service_execution(service_request)
        
        assert execution_proof is not None
        assert execution_proof.agent_id == agent.agent_id
        assert execution_proof.task_completed is True
        assert execution_proof.execution_time > 0
        assert "task_type" in execution_proof.results
        assert execution_proof.results["task_type"] == "competitor_analysis"
        assert execution_proof.results["ai_confidence_score"] > 0.8
        
        # Check metadata
        assert execution_proof.metadata["framework_version"] == "1.0.0"
        assert execution_proof.metadata["agent_type"] == "cardano_enhanced"
        assert execution_proof.metadata["compliance_verified"] is True
    
    @pytest.mark.asyncio
    async def test_cross_chain_demonstration(self, mock_agent):
        """Test cross-chain integration demonstration."""
        agent, mock_client = mock_agent
        
        # Mock cross-chain registration
        supported_chains = ["cardano", "ethereum", "polygon", "solana", "avalanche"]
        mock_client.register_cross_chain_service.return_value = {
            "status": "success",
            "agent_id": agent.agent_id,
            "supported_chains": supported_chains,
            "transaction_id": "tx_cross_chain_demo"
        }
        
        # Test cross-chain demonstration
        result = await agent._demonstrate_cross_chain(mock_client)
        
        assert result is not None
        assert result["operation"] == "cross_chain_service_discovery"
        assert "components" in result
        
        components = result["components"]
        
        # Check cross-chain registration
        assert "cross_chain_registration" in components
        registration = components["cross_chain_registration"]
        assert registration["agent_id"] == agent.agent_id
        assert registration["supported_chains"] == supported_chains
        assert registration["registration_result"]["status"] == "success"
        
        # Check capability metadata
        assert "capability_metadata" in components
        metadata = components["capability_metadata"]
        assert "cardano" in metadata
        assert "ethereum" in metadata
        assert "polygon" in metadata
        assert "solana" in metadata
        assert "avalanche" in metadata
        
        # Verify chain-specific capabilities
        cardano_caps = metadata["cardano"]
        assert "NMKR NFT minting" in cardano_caps["specializations"]
        assert "Native performance" == cardano_caps["performance"]
    
    @pytest.mark.asyncio
    async def test_demo_summary_generation(self, mock_agent):
        """Test demo summary generation."""
        agent, mock_client = mock_agent
        
        # Create sample phases data
        phases = {
            "agent_registration": {
                "operation": "agent_registration",
                "registration_result": {"status": "success"}
            },
            "service_marketplace": {
                "operation": "service_marketplace", 
                "components": {"service_discovery": {"status": "success"}}
            },
            "governance_economics": {
                "operation": "governance_economics",
                "components": {"revenue_distribution": {"status": "success"}}
            }
        }
        
        # Test summary generation
        summary = agent._generate_demo_summary(phases)
        
        assert summary is not None
        assert summary["total_phases"] == 3
        assert summary["successful_operations"] >= 0
        assert "blockchain_transactions" in summary
        assert "economic_model" in summary
        assert "compliance_level" in summary
        assert "cross_chain_support" in summary
        assert "key_innovations" in summary
        assert "technical_achievements" in summary
        
        # Check innovation list
        innovations = summary["key_innovations"]
        assert "Hierarchical agent registry with reputation staking" in innovations
        assert "Automated escrow with execution proof verification" in innovations
        assert "Revenue participation tokens for community rewards" in innovations
    
    @pytest.mark.asyncio
    async def test_browser_integration(self, mock_agent):
        """Test browser client integration."""
        agent, mock_client = mock_agent
        
        # The browser client is already mocked in the fixture
        # Test that it's properly configured
        assert agent.browser_client is not None
        
        # Test navigation
        response = await agent.browser_client.navigate("https://cardano.org")
        assert response is not None
        assert response["status"] == "success"
        assert "cardano" in response["content"].lower()


class TestCardanoAgentMCPIntegration:
    """Test MCP server integration with Cardano Enhanced Agent."""
    
    @pytest.fixture
    def mcp_config(self):
        """Create MCP-compatible configuration."""
        return {
            "agent_id": "mcp_cardano_enhanced",
            "owner_address": "addr1_mcp_test",
            "nmkr_api_key": "mcp_test_key",
            "blockfrost_project_id": "mcp_test_project"
        }
    
    @pytest.mark.asyncio
    async def test_mcp_agent_creation(self, mcp_config):
        """Test creating agent through MCP interface."""
        # Test agent creation with MCP-style parameters
        agent = CardanoEnhancedAgent(
            name="mcp_cardano_test",
            config=mcp_config
        )
        
        assert agent.agent_id == mcp_config["agent_id"]
        assert agent.name == "mcp_cardano_test"
        
        # Test that agent can be used in async context (MCP requirement)
        async with agent:
            assert agent.browser_client is not None
    
    @pytest.mark.asyncio
    async def test_mcp_operation_interface(self, mcp_config):
        """Test MCP-compatible operation interface."""
        with patch('examples.cardano_enhanced_agent.EnhancedCardanoClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)
            
            # Mock successful operations
            mock_client.register_agent.return_value = {"status": "success", "agent_id": "mcp_test"}
            
            agent = CardanoEnhancedAgent(name="mcp_test", config=mcp_config)
            agent.browser_client = AsyncMock()
            
            # Test MCP-style operation call
            result = await agent.run(
                operation="register",
                stake_amount=500.0
            )
            
            assert result is not None
            assert result["operation"] == "agent_registration"
            
            # Test default operation
            result = await agent.run()  # Should default to full_demo
            assert result is not None


class TestCardanoAgentRealIntegration:
    """Test real integration scenarios (with mocked external services)."""
    
    @pytest.mark.asyncio
    async def test_complete_agent_lifecycle(self):
        """Test complete agent lifecycle from registration to reward claiming."""
        config = {
            "agent_id": "lifecycle_test_agent",
            "owner_address": "addr1_lifecycle_test",
            "nmkr_api_key": "lifecycle_test_key",
            "blockfrost_project_id": "lifecycle_test_project"
        }
        
        with patch('examples.cardano_enhanced_agent.EnhancedCardanoClient') as mock_client_class:
            # Create comprehensive mock client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)
            
            # Mock complete lifecycle operations
            mock_client.register_agent.return_value = {
                "status": "success",
                "agent_id": "lifecycle_test_agent",
                "stake_tier": "professional",
                "transaction_id": "tx_lifecycle_register"
            }
            
            mock_client.find_agents.return_value = [
                {
                    "agent_id": "lifecycle_test_agent",
                    "reputation_score": 0.85,
                    "capabilities": ["web_automation", "blockchain"]
                }
            ]
            
            mock_client.create_escrow.return_value = {
                "status": "success",
                "escrow_id": "lifecycle_escrow",
                "transaction_id": "tx_lifecycle_escrow"
            }
            
            mock_client.release_escrow.return_value = {
                "status": "success",
                "escrow_id": "lifecycle_escrow",
                "payment_released": 100.0,
                "reputation_updated": True
            }
            
            mock_client.distribute_revenue.return_value = {
                "status": "success",
                "total_revenue": 1000.0,
                "total_recipients": 1
            }
            
            mock_client.claim_rewards.return_value = {
                "status": "success",
                "claimed_amount": 50.0,
                "transaction_id": "tx_lifecycle_claim"
            }
            
            mock_client.register_cross_chain_service.return_value = {
                "status": "success",
                "supported_chains": ["cardano", "ethereum"],
                "transaction_id": "tx_lifecycle_cross_chain"
            }
            
            # Create and test agent
            agent = CardanoEnhancedAgent(name="lifecycle_test", config=config)
            agent.browser_client = AsyncMock()
            agent.browser_client.navigate.return_value = {
                "page_title": "Test Page",
                "content": "test content",
                "status": "success"
            }
            
            # Run complete lifecycle
            result = await agent.run("full_demo")
            
            # Verify complete lifecycle execution
            assert result is not None
            assert result["demo_type"] == "full_cardano_ai_economy"
            assert len(result["phases"]) == 5
            assert "summary" in result
            
            # Verify all operations were called
            mock_client.register_agent.assert_called_once()
            mock_client.find_agents.assert_called()
            mock_client.create_escrow.assert_called_once()
            mock_client.release_escrow.assert_called_once()
            mock_client.distribute_revenue.assert_called_once()
            mock_client.claim_rewards.assert_called()
            mock_client.register_cross_chain_service.assert_called_once()


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "--tb=short"])
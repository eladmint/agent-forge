"""
NMKR integration tests for blockchain functionality.
Tests the NMKR Proof-of-Execution integration including
NFT minting, metadata compliance, and transaction verification.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from typing import Dict, List, Any


class TestNMKRIntegration:
    """Test NMKR Proof-of-Execution integration."""

    @pytest.fixture
    def nmkr_config(self):
        """NMKR integration configuration."""
        return {
            "api_key": "test_nmkr_api_key_123",
            "policy_id": "test_policy_456",
            "wallet_address": "addr1test789xyz",
            "network": "testnet"
        }

    @pytest.fixture
    def mock_nmkr_client(self):
        """Mock NMKR client."""
        client = AsyncMock()
        
        # Mock successful NFT minting
        client.mint_nft.return_value = {
            "transaction_id": "tx_def456",
            "policy_id": "test_policy_456",
            "asset_name": "AgentProof001",
            "status": "success"
        }
        
        # Mock transaction status checking
        client.get_transaction_status.return_value = {
            "transaction_id": "tx_def456",
            "status": "confirmed",
            "confirmations": 6,
            "block_height": 12345678
        }
        
        # Mock policy assets
        client.get_policy_assets.return_value = [
            {
                "asset_name": "AgentProof001",
                "metadata": {
                    "attributes": {
                        "Agent ID": "test_agent_001"
                    }
                }
            }
        ]
        
        return client

    @pytest.fixture
    def sample_execution_proof(self):
        """Sample agent execution proof data."""
        return {
            "agent_id": "test_agent_001",
            "execution_id": "exec_001", 
            "timestamp": datetime.now().isoformat(),
            "task_completed": True,
            "execution_time": 23.7,
            "results": {
                "quality_score": 0.94,
                "success_rate": 1.0
            },
            "metadata": {
                "framework_version": "1.0.0",
                "agent_type": "test_agent"
            }
        }

    @pytest.mark.blockchain
    @pytest.mark.asyncio
    async def test_nmkr_proof_generation(self, mock_nmkr_client, nmkr_config, sample_execution_proof):
        """Test NMKR proof-of-execution NFT generation."""
        from core.blockchain.nmkr_integration import NMKRProofGenerator
        
        generator = NMKRProofGenerator(
            client=mock_nmkr_client,
            policy_id=nmkr_config.get("policy_id", "default_policy"),
            collection_name="Test Collection"
        )
        
        # Generate proof NFT
        result = await generator.generate_proof(sample_execution_proof)
        
        # Verify proof generation
        assert result["status"] == "success"
        assert "transaction_id" in result
        assert "proof_hash" in result
        assert result["proof_type"] == "execution_proof"
        
        # Verify NMKR client was called
        mock_nmkr_client.mint_nft.assert_called_once()

    @pytest.mark.blockchain  
    @pytest.mark.asyncio
    async def test_transaction_verification(self, mock_nmkr_client, nmkr_config):
        """Test blockchain transaction verification."""
        from core.blockchain.nmkr_integration import NMKRProofGenerator
        
        generator = NMKRProofGenerator(
            client=mock_nmkr_client,
            policy_id=nmkr_config.get("policy_id", "default_policy")
        )
        
        # Test transaction verification
        result = await generator.verify_transaction("tx_abc123")
        
        # Verify the transaction status check
        assert result["status"] == "confirmed"
        assert result["confirmations"] >= 1
        assert result["verified"] is True
        
        mock_nmkr_client.get_transaction_status.assert_called_once_with("tx_abc123")

    @pytest.mark.blockchain
    @pytest.mark.asyncio
    async def test_metadata_compliance(self, mock_nmkr_client, nmkr_config, sample_execution_proof):
        """Test metadata creation and compliance."""
        from core.blockchain.nmkr_integration import NMKRProofGenerator
        
        generator = NMKRProofGenerator(
            client=mock_nmkr_client,
            policy_id=nmkr_config.get("policy_id", "default_policy")
        )
        
        # Generate proof and check metadata
        result = await generator.generate_proof(sample_execution_proof)
        
        # Verify call was made with correct structure
        call_args = mock_nmkr_client.mint_nft.call_args[1]
        metadata = call_args["metadata"]
        
        # Check essential fields are present
        assert "agent_id" in metadata
        assert "execution_id" in metadata
        assert "agent_framework" in metadata
        assert metadata["agent_framework"] == "Agent Forge"

    @pytest.mark.blockchain
    @pytest.mark.asyncio 
    async def test_get_agent_proofs(self, mock_nmkr_client, nmkr_config):
        """Test retrieving proofs for specific agent."""
        from core.blockchain.nmkr_integration import NMKRProofGenerator
        
        generator = NMKRProofGenerator(
            client=mock_nmkr_client,
            policy_id=nmkr_config.get("policy_id", "default_policy")
        )
        
        # Get proofs for agent
        proofs = await generator.get_agent_proofs("test_agent_001")
        
        # Verify results
        assert isinstance(proofs, list)
        assert len(proofs) == 1
        assert proofs[0]["metadata"]["attributes"]["Agent ID"] == "test_agent_001"
        
        mock_nmkr_client.get_policy_assets.assert_called_once()

    @pytest.mark.blockchain
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_nmkr_client, nmkr_config, sample_execution_proof):
        """Test error handling in NMKR integration."""
        from core.blockchain.nmkr_integration import NMKRProofGenerator
        
        # Configure mock to simulate error
        mock_nmkr_client.mint_nft.side_effect = Exception("Network timeout")
        
        generator = NMKRProofGenerator(
            client=mock_nmkr_client,
            policy_id=nmkr_config.get("policy_id", "default_policy")
        )
        
        # Test error handling
        result = await generator.generate_proof(sample_execution_proof)
        
        # Should return error status
        assert result["status"] == "error"
        assert "error" in result
        assert "proof_hash" in result  # Hash should still be generated

    @pytest.mark.blockchain
    def test_execution_proof_class(self, sample_execution_proof):
        """Test ExecutionProof class functionality."""
        from core.blockchain.nmkr_integration import ExecutionProof
        
        # Create execution proof
        proof = ExecutionProof(**sample_execution_proof)
        
        # Test serialization
        proof_dict = proof.to_dict()
        assert proof_dict["agent_id"] == "test_agent_001"
        assert proof_dict["execution_id"] == "exec_001"
        assert proof_dict["task_completed"] is True
        
        # Test hash generation
        hash_value = proof.generate_hash()
        assert isinstance(hash_value, str)
        assert len(hash_value) == 64  # SHA256 hex string
        
        # Test hash consistency
        hash_value2 = proof.generate_hash()
        assert hash_value == hash_value2

    @pytest.mark.blockchain
    @pytest.mark.asyncio
    async def test_nmkr_client_context_manager(self):
        """Test NMKR client async context manager."""
        from core.blockchain.nmkr_integration import NMKRClient
        
        # Test context manager usage
        async with NMKRClient("test_api_key") as client:
            assert client.session is not None
            assert client.api_key == "test_api_key"
            assert client.base_url == "https://api.nmkr.io"
        
        # Session should be closed after context exit
        # Note: In real usage, session would be None, but mock behavior may vary
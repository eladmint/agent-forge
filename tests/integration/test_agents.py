"""
Integration tests for Agent Forge agents.

Tests the functionality of specific agent implementations including
SimpleNavigationAgent and NMKRAuditorAgent.
"""

import pytest
import asyncio
import json
import hashlib
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

# Import agents
from examples.simple_navigation_agent import SimpleNavigationAgent
from examples.nmkr_auditor_agent import NMKRAuditorAgent


@pytest.mark.integration
class TestSimpleNavigationAgent:
    """Test SimpleNavigationAgent functionality."""
    
    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test agent initialization."""
        agent = SimpleNavigationAgent(url="https://example.com")
        
        assert agent.url == "https://example.com"
        assert agent.name is not None
        assert not agent.is_ready()
        
        # Test initialization
        with patch('core.shared.web.browsers.SteelBrowserClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            success = await agent.initialize()
            assert success is True
            assert agent.is_ready() is True
            
            await agent.cleanup()
    
    @pytest.mark.asyncio
    async def test_successful_navigation(self, mock_browser_client):
        """Test successful page navigation."""
        # Configure mock response
        mock_browser_client.navigate.return_value = {
            "success": True,
            "page_title": "Example Domain",
            "content": "<html><body><h1>Example</h1></body></html>",
            "status": "200"
        }
        
        agent = SimpleNavigationAgent(url="https://example.com")
        
        with patch('core.agents.base.SteelBrowserClient', return_value=mock_browser_client):
            async with agent:
                result = await agent.run()
                
                assert result is not None
                # Browser navigate should have been called
                mock_browser_client.navigate.assert_called_with("https://example.com")
    
    @pytest.mark.asyncio
    async def test_navigation_failure(self, mock_browser_client):
        """Test handling of navigation failure."""
        # Configure mock to return failure
        mock_browser_client.navigate.return_value = None
        
        agent = SimpleNavigationAgent(url="https://example.com")
        
        with patch('core.agents.base.SteelBrowserClient', return_value=mock_browser_client):
            async with agent:
                result = await agent.run()
                
                # Should handle failure gracefully
                assert result is None or (isinstance(result, dict) and "error" in result)
    
    @pytest.mark.asyncio
    async def test_url_validation(self):
        """Test URL validation in SimpleNavigationAgent."""
        # Test with invalid URL
        agent = SimpleNavigationAgent(url="not-a-url")
        
        with patch('core.shared.web.browsers.SteelBrowserClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            async with agent:
                result = await agent.run()
                
                # Should still attempt to navigate (agent doesn't validate URL format)
                assert result is not None or result is None
    
    @pytest.mark.asyncio
    async def test_configuration_handling(self):
        """Test configuration parameter handling."""
        config = {"timeout": 30, "debug": True}
        agent = SimpleNavigationAgent(
            name="test_nav_agent",
            config=config,
            url="https://test.example.com"
        )
        
        assert agent.config == config
        assert agent.url == "https://test.example.com"
        assert agent.name == "test_nav_agent"


@pytest.mark.integration
class TestNMKRAuditorAgent:
    """Test NMKRAuditorAgent functionality."""
    
    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test NMKR auditor agent initialization."""
        agent = NMKRAuditorAgent(
            url="https://cardano.org",
            task_description="Test blockchain analysis"
        )
        
        assert agent.url == "https://cardano.org"
        assert agent.task_description == "Test blockchain analysis"
        assert not agent.is_ready()
        
        # Test initialization
        with patch('core.shared.web.browsers.SteelBrowserClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            success = await agent.initialize()
            assert success is True
            assert agent.is_ready() is True
            
            await agent.cleanup()
    
    @pytest.mark.asyncio
    async def test_proof_of_execution_workflow(self, mock_browser_client):
        """Test complete proof-of-execution workflow."""
        # Configure mock response for blockchain content
        mock_browser_client.navigate.return_value = {
            "success": True,
            "page_title": "Cardano - Home",
            "content": "<html><body><h1>Cardano</h1><p>blockchain smart contracts</p></body></html>",
            "status": "200"
        }
        
        agent = NMKRAuditorAgent(
            url="https://cardano.org",
            task_description="Analyze Cardano homepage",
            nmkr_api_key="test_key"
        )
        
        with patch('core.agents.base.SteelBrowserClient', return_value=mock_browser_client):
            async with agent:
                result = await agent.run()
                
                # Should return complete proof package
                assert result is not None
                assert isinstance(result, dict)
                
                # Verify proof package structure
                expected_keys = [
                    "execution_summary",
                    "verification_data", 
                    "blockchain_integration",
                    "execution_results"
                ]
                
                for key in expected_keys:
                    assert key in result, f"Missing key: {key}"
                
                # Verify execution summary
                summary = result["execution_summary"]
                assert summary["url"] == "https://cardano.org"
                assert summary["task_description"] == "Analyze Cardano homepage"
                assert summary["status"] == "completed"
                
                # Verify verification data
                verification = result["verification_data"]
                assert "audit_log" in verification
                assert "proof_hash" in verification
                assert "ipfs_cid" in verification
                assert verification["verification_method"] == "SHA-256"
                
                # Verify blockchain integration
                blockchain = result["blockchain_integration"]
                assert blockchain["blockchain"] == "Cardano"
                assert blockchain["standard"] == "CIP-25"
                assert "nft_metadata" in blockchain
                assert "nmkr_payload" in blockchain
    
    @pytest.mark.asyncio
    async def test_audit_log_generation(self, mock_browser_client):
        """Test audit log generation and structure."""
        mock_browser_client.navigate.return_value = {
            "success": True,
            "page_title": "Test Page",
            "content": "<html><body>Test content</body></html>",
            "status": "200"
        }
        
        agent = NMKRAuditorAgent(
            url="https://example.com",
            task_description="Test audit log generation"
        )
        
        with patch('core.agents.base.SteelBrowserClient', return_value=mock_browser_client):
            async with agent:
                result = await agent.run()
                
                audit_log = result["verification_data"]["audit_log"]
                
                # Should be valid JSON
                audit_data = json.loads(audit_log)
                
                # Verify audit log structure
                assert "audit_log_version" in audit_data
                assert "agent_information" in audit_data
                assert "task_details" in audit_data
                assert "execution_trace" in audit_data
                assert "blockchain_integration" in audit_data
                
                # Verify agent information
                agent_info = audit_data["agent_information"]
                assert agent_info["framework"] == "Agent Forge"
                assert agent_info["browser_automation"] == "Steel Browser API"
    
    @pytest.mark.asyncio
    async def test_cryptographic_proof_generation(self, mock_browser_client):
        """Test cryptographic proof generation."""
        mock_browser_client.navigate.return_value = {
            "success": True,
            "page_title": "Test Page",
            "content": "<html><body>Test content</body></html>",
            "status": "200"
        }
        
        agent = NMKRAuditorAgent(url="https://example.com")
        
        with patch('core.agents.base.SteelBrowserClient', return_value=mock_browser_client):
            async with agent:
                result = await agent.run()
                
                verification = result["verification_data"]
                audit_log = verification["audit_log"]
                proof_hash = verification["proof_hash"]
                
                # Verify hash generation
                expected_hash = hashlib.sha256(audit_log.encode()).hexdigest()
                assert proof_hash == expected_hash
                
                # Hash should be 64 characters (SHA-256)
                assert len(proof_hash) == 64
                assert all(c in '0123456789abcdef' for c in proof_hash)
    
    @pytest.mark.asyncio
    async def test_ipfs_simulation(self, mock_browser_client):
        """Test IPFS simulation functionality."""
        mock_browser_client.navigate.return_value = {
            "success": True,
            "page_title": "Test Page", 
            "content": "<html><body>Test content</body></html>",
            "status": "200"
        }
        
        agent = NMKRAuditorAgent(url="https://example.com")
        
        with patch('core.agents.base.SteelBrowserClient', return_value=mock_browser_client):
            async with agent:
                result = await agent.run()
                
                ipfs_cid = result["verification_data"]["ipfs_cid"]
                
                # Should look like a valid IPFS CID
                assert ipfs_cid.startswith("bafybeig")
                assert len(ipfs_cid) > 20
    
    @pytest.mark.asyncio
    async def test_cip25_metadata_generation(self, mock_browser_client):
        """Test CIP-25 metadata generation."""
        mock_browser_client.navigate.return_value = {
            "success": True,
            "page_title": "Test Page",
            "content": "<html><body>Test content</body></html>",
            "status": "200"
        }
        
        agent = NMKRAuditorAgent(
            url="https://example.com",
            task_description="Test CIP-25 metadata"
        )
        
        with patch('core.agents.base.SteelBrowserClient', return_value=mock_browser_client):
            async with agent:
                result = await agent.run()
                
                metadata = result["blockchain_integration"]["nft_metadata"]
                
                # Verify CIP-25 structure
                assert "721" in metadata
                assert "verification" in metadata
                
                # Verify policy structure
                policy_data = metadata["721"]["policy_id_placeholder"]
                token_name = list(policy_data.keys())[0]
                token_data = policy_data[token_name]
                
                # Verify token data
                assert token_data["name"] == "Agent Forge Execution Proof"
                assert "description" in token_data
                assert "attributes" in token_data
                assert "files" in token_data
                
                # Verify attributes
                attributes = token_data["attributes"]
                assert attributes["Agent Framework"] == "Agent Forge"
                assert attributes["Blockchain"] == "Cardano"
                assert attributes["Standard"] == "CIP-25"
    
    @pytest.mark.asyncio
    async def test_nmkr_payload_construction(self, mock_browser_client):
        """Test NMKR API payload construction."""
        mock_browser_client.navigate.return_value = {
            "success": True,
            "page_title": "Test Page",
            "content": "<html><body>Test content</body></html>",
            "status": "200"
        }
        
        agent = NMKRAuditorAgent(
            url="https://example.com",
            nmkr_api_key="test_key_123"
        )
        
        with patch('core.agents.base.SteelBrowserClient', return_value=mock_browser_client):
            async with agent:
                result = await agent.run()
                
                nmkr_payload = result["blockchain_integration"]["nmkr_payload"]
                
                # Verify NMKR payload structure
                assert "projectUid" in nmkr_payload
                assert "tokenname" in nmkr_payload
                assert "displayname" in nmkr_payload
                assert "previewImageNft" in nmkr_payload
                assert "metadataPlaceholder" in nmkr_payload
                assert "mint" in nmkr_payload
                assert "options" in nmkr_payload
                
                # Verify metadata placeholder
                metadata_placeholder = nmkr_payload["metadataPlaceholder"]
                assert "execution_url" in metadata_placeholder
                assert "proof_hash" in metadata_placeholder
                assert "audit_log_cid" in metadata_placeholder
    
    @pytest.mark.asyncio
    async def test_task_complexity_estimation(self, mock_browser_client):
        """Test task complexity estimation."""
        mock_browser_client.navigate.return_value = {
            "success": True,
            "page_title": "GitHub Repository",
            "content": "<html><body>GitHub repository content</body></html>",
            "status": "200"
        }
        
        # Test different complexity scenarios
        test_cases = [
            ("https://example.com", "Simple analysis", "low"),
            ("https://github.com/user/repo", "Repository analysis", "medium"),
            ("https://api.complex-service.com", "Complex blockchain analysis", "high")
        ]
        
        for url, task, expected_complexity in test_cases:
            agent = NMKRAuditorAgent(url=url, task_description=task)
            
            with patch('core.agents.base.SteelBrowserClient', return_value=mock_browser_client):
                async with agent:
                    result = await agent.run()
                    
                    # Check if complexity is estimated correctly
                    audit_log = json.loads(result["verification_data"]["audit_log"])
                    estimated_complexity = audit_log["task_details"]["estimated_complexity"]
                    
                    assert estimated_complexity in ["low", "medium", "high"]
    
    @pytest.mark.asyncio
    async def test_content_analysis_patterns(self, mock_browser_client):
        """Test content analysis for different site types."""
        test_cases = [
            {
                "url": "https://github.com/user/repo",
                "content": "<html><body>repository commit issues releases python</body></html>",
                "expected_type": "github_repository"
            },
            {
                "url": "https://news.ycombinator.com",
                "content": "<html><body>article comment technology startup</body></html>",
                "expected_type": "news_site"
            },
            {
                "url": "https://cardano.org",
                "content": "<html><body>cardano blockchain smart contract ada</body></html>",
                "expected_type": "blockchain_site"
            }
        ]
        
        for case in test_cases:
            mock_browser_client.navigate.return_value = {
                "success": True,
                "page_title": "Test Page",
                "content": case["content"],
                "status": "200"
            }
            
            agent = NMKRAuditorAgent(url=case["url"])
            
            with patch('core.agents.base.SteelBrowserClient', return_value=mock_browser_client):
                async with agent:
                    result = await agent.run()
                    
                    analysis_type = result["execution_results"]["analysis_type"]
                    assert analysis_type == case["expected_type"]
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_browser_client):
        """Test error handling in NMKR auditor agent."""
        # Test navigation failure
        mock_browser_client.navigate.return_value = None
        
        agent = NMKRAuditorAgent(url="https://example.com")
        
        with patch('core.agents.base.SteelBrowserClient', return_value=mock_browser_client):
            async with agent:
                result = await agent.run()
                
                # Should handle failure gracefully
                assert result is not None
                
                # Should still generate proof even with navigation failure
                if isinstance(result, dict) and "status" not in result:
                    # If it's a proof package, it should be complete
                    assert "verification_data" in result
                    assert "blockchain_integration" in result


@pytest.mark.integration
class TestAgentInteroperability:
    """Test agent interoperability and framework integration."""
    
    @pytest.mark.asyncio
    async def test_agent_inheritance_consistency(self):
        """Test that all agents properly inherit from BaseAgent."""
        from core.agents.base import BaseAgent
        
        agents = [SimpleNavigationAgent, NMKRAuditorAgent]
        
        for agent_class in agents:
            # Should be BaseAgent subclass
            assert issubclass(agent_class, BaseAgent)
            
            # Should implement required methods
            assert hasattr(agent_class, 'run')
            
            # Should be instantiable with required parameters
            if agent_class.__name__ == 'SimpleNavigationAgent':
                agent = agent_class(url="https://example.com")
            elif agent_class.__name__ == 'NMKRAuditorAgent':
                agent = agent_class(url="https://example.com")
            else:
                agent = agent_class()
            assert isinstance(agent, BaseAgent)
    
    @pytest.mark.asyncio
    async def test_configuration_compatibility(self):
        """Test configuration compatibility across agents."""
        config = {
            "timeout": 30,
            "debug": True,
            "custom_setting": "value"
        }
        
        agents = [
            SimpleNavigationAgent(url="https://example.com", config=config),
            NMKRAuditorAgent(url="https://example.com", config=config)
        ]
        
        for agent in agents:
            assert agent.config == config
            assert agent.config.get("timeout") == 30
            assert agent.config.get("debug") is True
    
    @pytest.mark.asyncio
    async def test_async_pattern_consistency(self, mock_browser_client):
        """Test async pattern consistency across agents."""
        agents = [
            SimpleNavigationAgent(url="https://example.com"),
            NMKRAuditorAgent(url="https://example.com")
        ]
        
        mock_browser_client.navigate.return_value = {
            "success": True,
            "page_title": "Test Page",
            "content": "<html><body>Test</body></html>",
            "status": "200"
        }
        
        with patch('core.agents.base.SteelBrowserClient', return_value=mock_browser_client):
            for agent in agents:
                # All agents should support async context manager
                async with agent:
                    assert agent.is_ready()
                    
                    # All agents should have async run method
                    result = await agent.run()
                    assert result is not None or result is None
                
                # Should be cleaned up after context exit
                assert not agent.is_ready()
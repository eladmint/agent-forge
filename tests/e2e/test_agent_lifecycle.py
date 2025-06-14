"""
End-to-end tests for complete agent lifecycle.
Tests the full agent workflow from initialization through
task execution to cleanup and blockchain integration.
"""

import pytest
import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from typing import Dict, List, Any


class TestAgentLifecycleE2E:
    """End-to-end agent lifecycle testing."""

    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            
            # Create test configuration
            config = {
                "agent_id": "e2e_test_agent",
                "type": "scraper",
                "browser_config": {
                    "headless": True,
                    "timeout": 30,
                    "viewport": {"width": 1920, "height": 1080}
                },
                "extraction_config": {
                    "max_pages": 5,
                    "rate_limit": 1.0,
                    "retry_attempts": 3
                },
                "blockchain_config": {
                    "enabled": True,
                    "proof_generation": True,
                    "nmkr_integration": True
                }
            }
            
            config_file = workspace / "agent_config.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            yield workspace, config

    @pytest.fixture
    def mock_external_services(self):
        """Mock external services for E2E testing."""
        services = {
            "browser": AsyncMock(),
            "nmkr_client": AsyncMock(),
            "masumi_client": AsyncMock()
        }
        
        # Configure browser mock
        services["browser"].navigate.return_value = {
            "status": "success",
            "url": "https://example.com",
            "title": "Example Site",
            "load_time": 1.2
        }
        
        services["browser"].extract_data.return_value = {
            "data": [
                {"title": "Item 1", "url": "https://example.com/item1"},
                {"title": "Item 2", "url": "https://example.com/item2"},
                {"title": "Item 3", "url": "https://example.com/item3"}
            ],
            "metadata": {
                "page_title": "Example Site",
                "extraction_timestamp": datetime.now().isoformat(),
                "total_items": 3
            }
        }
        
        # Configure NMKR mock
        services["nmkr_client"].mint_nft.return_value = {
            "transaction_id": "tx_e2e_test_123",
            "policy_id": "policy_e2e_456",
            "asset_name": "AgentProofE2E001",
            "status": "submitted"
        }
        
        # Configure Masumi mock
        services["masumi_client"].register_agent.return_value = {
            "agent_id": "masumi_e2e_agent_001",
            "registration_status": "active",
            "api_key": "api_key_e2e_789"
        }
        
        return services

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_complete_agent_lifecycle(self, temp_workspace, mock_external_services):
        """Test complete agent lifecycle from creation to cleanup."""
        workspace, config = temp_workspace
        
        from core.agents.base_agent import AsyncContextAgent
        from core.blockchain.nmkr_integration import NMKRProofGenerator
        
        # Phase 1: Agent Creation and Initialization
        agent = AsyncContextAgent(
            name=config["agent_id"],
            config=config,
            browser_client=mock_external_services["browser"]
        )
        
        # Initialize agent
        await agent.initialize()
        
        # Verify initialization
        assert agent.is_initialized is True
        assert agent.name == "e2e_test_agent"
        assert agent.config["type"] == "scraper"
        
        # Phase 2: Task Execution
        task_results = []
        
        # Execute navigation task
        nav_result = await agent.navigate("https://example.com")
        task_results.append(nav_result)
        
        assert nav_result["status"] == "success"
        assert nav_result["url"] == "https://example.com"
        
        # Execute data extraction task
        extraction_result = await agent.extract_data("div.content")
        task_results.append(extraction_result)
        
        assert len(extraction_result["data"]) == 3
        assert extraction_result["metadata"]["total_items"] == 3
        
        # Phase 3: Blockchain Integration
        if config["blockchain_config"]["enabled"]:
            proof_generator = NMKRProofGenerator(
                client=mock_external_services["nmkr_client"]
            )
            
            # Generate execution proof
            execution_proof = {
                "agent_id": agent.name,
                "execution_id": f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "task_completed": True,
                "execution_time": 5.2,
                "results": {
                    "pages_scraped": 1,
                    "data_extracted": 3,
                    "quality_score": 0.95
                },
                "tasks_executed": task_results
            }
            
            proof_result = await proof_generator.generate_proof(execution_proof)
            
            assert proof_result["status"] == "success"
            assert proof_result["transaction_id"] == "tx_e2e_test_123"
        
        # Phase 4: Results Compilation and Storage
        final_results = {
            "agent_id": agent.name,
            "execution_summary": {
                "start_time": datetime.now().isoformat(),
                "tasks_completed": len(task_results),
                "total_items_extracted": 3,
                "success_rate": 1.0
            },
            "task_results": task_results,
            "blockchain_proof": proof_result if config["blockchain_config"]["enabled"] else None
        }
        
        # Save results to workspace
        results_file = workspace / "execution_results.json"
        with open(results_file, 'w') as f:
            json.dump(final_results, f, indent=2, default=str)
        
        assert results_file.exists()
        
        # Phase 5: Agent Cleanup
        await agent.cleanup()
        
        # Verify cleanup
        assert agent.is_initialized is False
        
        # Verify all mocks were called appropriately
        mock_external_services["browser"].navigate.assert_called_once()
        mock_external_services["browser"].extract_data.assert_called_once()
        
        if config["blockchain_config"]["enabled"]:
            mock_external_services["nmkr_client"].mint_nft.assert_called_once()

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_multi_page_scraping_workflow(self, temp_workspace, mock_external_services):
        """Test complete multi-page scraping workflow."""
        workspace, config = temp_workspace
        
        from core.agents.base_agent import AsyncContextAgent
        
        # Configure browser mock for multi-page scenario
        urls = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3"
        ]
        
        # Mock different responses for each page
        def mock_navigate(url):
            page_num = url.split('page')[1] if 'page' in url else '1'
            return {
                "status": "success",
                "url": url,
                "title": f"Page {page_num}",
                "load_time": 1.0
            }
        
        def mock_extract_data(selector):
            return {
                "data": [
                    {"item": f"Item A from {selector}", "value": "value_a"},
                    {"item": f"Item B from {selector}", "value": "value_b"}
                ],
                "metadata": {
                    "selector": selector,
                    "extraction_timestamp": datetime.now().isoformat(),
                    "total_items": 2
                }
            }
        
        mock_external_services["browser"].navigate.side_effect = mock_navigate
        mock_external_services["browser"].extract_data.side_effect = mock_extract_data
        
        # Initialize agent
        agent = AsyncContextAgent(
            name="multi_page_agent",
            config=config,
            browser_client=mock_external_services["browser"]
        )
        
        await agent.initialize()
        
        # Execute multi-page workflow
        all_results = []
        
        for i, url in enumerate(urls):
            # Navigate to page
            nav_result = await agent.navigate(url)
            assert nav_result["status"] == "success"
            
            # Extract data from page
            data_result = await agent.extract_data(f"div.content-{i+1}")
            all_results.extend(data_result["data"])
            
            # Add delay between pages (rate limiting)
            await asyncio.sleep(0.1)
        
        # Verify multi-page results
        assert len(all_results) == 6  # 2 items per page × 3 pages
        assert mock_external_services["browser"].navigate.call_count == 3
        assert mock_external_services["browser"].extract_data.call_count == 3
        
        # Compile final results
        final_results = {
            "workflow_type": "multi_page_scraping",
            "pages_processed": len(urls),
            "total_items_extracted": len(all_results),
            "all_data": all_results,
            "execution_timestamp": datetime.now().isoformat()
        }
        
        # Save results
        results_file = workspace / "multi_page_results.json"
        with open(results_file, 'w') as f:
            json.dump(final_results, f, indent=2, default=str)
        
        await agent.cleanup()

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, temp_workspace, mock_external_services):
        """Test agent error recovery and resilience."""
        workspace, config = temp_workspace
        
        from core.agents.base_agent import AsyncContextAgent
        
        # Configure mock to simulate errors and recovery
        call_count = {"navigate": 0, "extract": 0}
        
        def mock_navigate_with_errors(url):
            call_count["navigate"] += 1
            if call_count["navigate"] <= 2:
                # First two calls fail
                raise Exception(f"Network error on attempt {call_count['navigate']}")
            else:
                # Third call succeeds
                return {
                    "status": "success",
                    "url": url,
                    "title": "Recovered Page",
                    "load_time": 1.5
                }
        
        def mock_extract_with_errors(selector):
            call_count["extract"] += 1
            if call_count["extract"] == 1:
                # First extraction fails
                raise Exception("Selector not found")
            else:
                # Second extraction succeeds
                return {
                    "data": [{"recovered": "data", "selector": selector}],
                    "metadata": {
                        "recovery_attempt": True,
                        "extraction_timestamp": datetime.now().isoformat()
                    }
                }
        
        mock_external_services["browser"].navigate.side_effect = mock_navigate_with_errors
        mock_external_services["browser"].extract_data.side_effect = mock_extract_with_errors
        
        # Initialize agent with retry configuration
        retry_config = config.copy()
        retry_config["extraction_config"]["retry_attempts"] = 3
        retry_config["extraction_config"]["retry_delay"] = 0.1
        
        agent = AsyncContextAgent(
            name="error_recovery_agent",
            config=retry_config,
            browser_client=mock_external_services["browser"]
        )
        
        await agent.initialize()
        
        # Test navigation with retry
        nav_result = await agent.navigate_with_retry("https://example.com/error-prone")
        
        # Should succeed after retries
        assert nav_result["status"] == "success"
        assert nav_result["title"] == "Recovered Page"
        assert call_count["navigate"] == 3  # Failed twice, succeeded on third
        
        # Test extraction with retry
        extract_result = await agent.extract_data_with_retry("div.error-prone")
        
        # Should succeed after retry
        assert len(extract_result["data"]) == 1
        assert extract_result["data"][0]["recovered"] == "data"
        assert call_count["extract"] == 2  # Failed once, succeeded on second
        
        # Log error recovery statistics
        recovery_stats = {
            "navigation_attempts": call_count["navigate"],
            "extraction_attempts": call_count["extract"],
            "final_status": "success",
            "error_recovery": True
        }
        
        stats_file = workspace / "error_recovery_stats.json"
        with open(stats_file, 'w') as f:
            json.dump(recovery_stats, f, indent=2)
        
        await agent.cleanup()

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_blockchain_integration_workflow(self, temp_workspace, mock_external_services):
        """Test complete blockchain integration workflow."""
        workspace, config = temp_workspace
        
        from core.agents.base_agent import AsyncContextAgent
        from core.blockchain.nmkr_integration import NMKRProofGenerator
        from core.blockchain.masumi_integration import MasumiAgentRegistrar
        
        # Initialize agent with blockchain enabled
        agent = AsyncContextAgent(
            name="blockchain_agent",
            config=config,
            browser_client=mock_external_services["browser"]
        )
        
        await agent.initialize()
        
        # Phase 1: Execute standard agent tasks
        nav_result = await agent.navigate("https://blockchain-test.com")
        data_result = await agent.extract_data("div.blockchain-data")
        
        # Phase 2: NMKR Proof Generation
        proof_generator = NMKRProofGenerator(
            client=mock_external_services["nmkr_client"]
        )
        
        execution_data = {
            "agent_id": agent.name,
            "execution_id": "blockchain_test_001",
            "timestamp": datetime.now().isoformat(),
            "task_completed": True,
            "execution_time": 3.7,
            "results": {
                "pages_scraped": 1,
                "data_extracted": len(data_result["data"]),
                "quality_score": 0.92
            },
            "blockchain_metadata": {
                "proof_type": "execution_verification",
                "framework": "Agent Forge",
                "version": "1.0.0"
            }
        }
        
        nmkr_result = await proof_generator.generate_proof(execution_data)
        
        assert nmkr_result["status"] == "success"
        assert nmkr_result["transaction_id"] == "tx_e2e_test_123"
        
        # Phase 3: Masumi Network Registration
        masumi_registrar = MasumiAgentRegistrar(
            client=mock_external_services["masumi_client"]
        )
        
        agent_profile = {
            "name": "E2E Blockchain Test Agent",
            "description": "End-to-end testing agent with blockchain integration",
            "category": "testing",
            "capabilities": ["web_scraping", "blockchain_integration", "proof_generation"],
            "pricing": {
                "base_rate": "5.0",
                "currency": "ADA",
                "billing_type": "per_execution"
            },
            "framework": "Agent Forge"
        }
        
        masumi_result = await masumi_registrar.register_agent(agent_profile)
        
        assert masumi_result["status"] == "success"
        assert masumi_result["agent_id"] == "masumi_e2e_agent_001"
        
        # Phase 4: Compile blockchain workflow results
        blockchain_results = {
            "workflow_type": "blockchain_integration",
            "agent_execution": {
                "navigation": nav_result,
                "data_extraction": data_result
            },
            "nmkr_proof": nmkr_result,
            "masumi_registration": masumi_result,
            "workflow_timestamp": datetime.now().isoformat(),
            "blockchain_enabled": True
        }
        
        # Save blockchain workflow results
        blockchain_file = workspace / "blockchain_workflow_results.json"
        with open(blockchain_file, 'w') as f:
            json.dump(blockchain_results, f, indent=2, default=str)
        
        # Verify blockchain integration completeness
        assert blockchain_file.exists()
        
        # Verify all blockchain services were called
        mock_external_services["nmkr_client"].mint_nft.assert_called_once()
        mock_external_services["masumi_client"].register_agent.assert_called_once()
        
        await agent.cleanup()

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_concurrent_agents_workflow(self, temp_workspace, mock_external_services):
        """Test workflow with multiple concurrent agents."""
        workspace, config = temp_workspace
        
        from core.agents.base_agent import AsyncContextAgent
        
        # Create multiple agent configurations
        agent_configs = []
        for i in range(3):
            agent_config = config.copy()
            agent_config["agent_id"] = f"concurrent_agent_{i+1}"
            agent_config["target_urls"] = [f"https://site{i+1}.com/page{j+1}" for j in range(2)]
            agent_configs.append(agent_config)
        
        # Configure mock for concurrent scenario
        def mock_navigate_concurrent(url):
            site_id = url.split('site')[1].split('.')[0] if 'site' in url else '1'
            page_id = url.split('page')[1] if 'page' in url else '1'
            return {
                "status": "success",
                "url": url,
                "title": f"Site {site_id} Page {page_id}",
                "load_time": 0.8
            }
        
        def mock_extract_concurrent(selector):
            return {
                "data": [
                    {"concurrent_item": f"Item from {selector}", "timestamp": datetime.now().isoformat()}
                ],
                "metadata": {
                    "concurrent_extraction": True,
                    "selector": selector
                }
            }
        
        mock_external_services["browser"].navigate.side_effect = mock_navigate_concurrent
        mock_external_services["browser"].extract_data.side_effect = mock_extract_concurrent
        
        async def run_agent_workflow(agent_config: Dict[str, Any]):
            """Run individual agent workflow."""
            agent = AsyncContextAgent(
                name=agent_config["agent_id"],
                config=agent_config,
                browser_client=mock_external_services["browser"]
            )
            
            await agent.initialize()
            
            agent_results = []
            
            for url in agent_config["target_urls"]:
                nav_result = await agent.navigate(url)
                data_result = await agent.extract_data("div.concurrent-content")
                
                agent_results.append({
                    "url": url,
                    "navigation": nav_result,
                    "extraction": data_result
                })
                
                # Small delay between pages
                await asyncio.sleep(0.05)
            
            await agent.cleanup()
            
            return {
                "agent_id": agent_config["agent_id"],
                "results": agent_results,
                "completion_time": datetime.now().isoformat()
            }
        
        # Run all agents concurrently
        start_time = datetime.now()
        
        concurrent_tasks = [run_agent_workflow(config) for config in agent_configs]
        all_agent_results = await asyncio.gather(*concurrent_tasks)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Compile concurrent workflow results
        concurrent_results = {
            "workflow_type": "concurrent_agents",
            "num_agents": len(agent_configs),
            "total_execution_time": execution_time,
            "agents_per_second": len(agent_configs) / execution_time,
            "agent_results": all_agent_results,
            "workflow_timestamp": end_time.isoformat()
        }
        
        # Save concurrent workflow results
        concurrent_file = workspace / "concurrent_workflow_results.json"
        with open(concurrent_file, 'w') as f:
            json.dump(concurrent_results, f, indent=2, default=str)
        
        # Verify concurrent execution
        assert len(all_agent_results) == 3
        assert all(result["agent_id"].startswith("concurrent_agent_") for result in all_agent_results)
        assert execution_time < 10.0  # Should complete within reasonable time
        
        # Verify all agents completed successfully
        for agent_result in all_agent_results:
            assert len(agent_result["results"]) == 2  # 2 URLs per agent
            for page_result in agent_result["results"]:
                assert page_result["navigation"]["status"] == "success"
                assert len(page_result["extraction"]["data"]) > 0

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_agent_state_persistence(self, temp_workspace, mock_external_services):
        """Test agent state persistence and recovery."""
        workspace, config = temp_workspace
        
        from core.agents.base_agent import AsyncContextAgent
        
        # Phase 1: Create agent and execute partial workflow
        agent = AsyncContextAgent(
            name="persistent_agent",
            config=config,
            browser_client=mock_external_services["browser"]
        )
        
        await agent.initialize()
        
        # Execute some tasks and save state
        nav_result = await agent.navigate("https://persistence-test.com")
        
        # Save agent state
        agent_state = {
            "agent_id": agent.name,
            "initialization_time": datetime.now().isoformat(),
            "completed_tasks": ["navigation"],
            "current_url": nav_result["url"],
            "pending_tasks": ["data_extraction", "blockchain_proof"],
            "execution_context": {
                "session_id": "persistence_test_001",
                "workflow_stage": "mid_execution"
            }
        }
        
        state_file = workspace / "agent_state.json"
        with open(state_file, 'w') as f:
            json.dump(agent_state, f, indent=2, default=str)
        
        # Simulate agent shutdown
        await agent.cleanup()
        
        # Phase 2: Restore agent from saved state
        with open(state_file, 'r') as f:
            restored_state = json.load(f)
        
        # Create new agent instance from saved state
        restored_agent = AsyncContextAgent(
            name=restored_state["agent_id"],
            config=config,
            browser_client=mock_external_services["browser"]
        )
        
        await restored_agent.initialize()
        
        # Continue from where we left off
        assert restored_state["current_url"] == "https://persistence-test.com"
        assert "data_extraction" in restored_state["pending_tasks"]
        
        # Complete remaining tasks
        data_result = await restored_agent.extract_data("div.persistent-content")
        
        # Update state
        final_state = restored_state.copy()
        final_state["completed_tasks"].extend(["data_extraction"])
        final_state["pending_tasks"].remove("data_extraction")
        final_state["completion_time"] = datetime.now().isoformat()
        final_state["final_results"] = {
            "navigation": nav_result,
            "extraction": data_result
        }
        
        # Save final state
        final_state_file = workspace / "agent_final_state.json"
        with open(final_state_file, 'w') as f:
            json.dump(final_state, f, indent=2, default=str)
        
        await restored_agent.cleanup()
        
        # Verify state persistence workflow
        assert final_state_file.exists()
        assert len(final_state["completed_tasks"]) == 2
        assert "data_extraction" not in final_state["pending_tasks"]
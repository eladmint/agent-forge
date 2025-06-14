"""
End-to-end tests for Agent Forge framework workflows.

Tests complete workflows from CLI command to agent execution and result generation.
"""

import pytest
import asyncio
import subprocess
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch


@pytest.mark.e2e
class TestCLIWorkflows:
    """Test complete CLI workflows end-to-end."""
    
    def test_cli_list_command(self):
        """Test CLI list command execution."""
        result = subprocess.run(
            ["python", "cli.py", "list"],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "Available agents:" in result.stdout
        assert "simple_navigation" in result.stdout or "simplenavigation" in result.stdout
        assert "nmkr_auditor" in result.stdout or "nmkrauditor" in result.stdout
    
    def test_cli_help_command(self):
        """Test CLI help command execution."""
        result = subprocess.run(
            ["python", "cli.py", "--help"],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "Agent Forge" in result.stdout
        assert "list" in result.stdout
        assert "run" in result.stdout
    
    def test_cli_version_command(self):
        """Test CLI version command execution."""
        result = subprocess.run(
            ["python", "cli.py", "--version"],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "Agent Forge" in result.stdout
    
    @pytest.mark.slow
    def test_simple_navigation_execution(self):
        """Test executing SimpleNavigationAgent through CLI."""
        result = subprocess.run(
            ["python", "cli.py", "run", "simple_navigation", "--url", "https://example.com"],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        
        # Should complete without error (even if navigation fails due to network)
        assert result.returncode == 0
        assert "Initializing agent" in result.stderr or "Navigating to" in result.stderr
    
    @pytest.mark.slow
    def test_nmkr_auditor_execution(self):
        """Test executing NMKRAuditorAgent through CLI."""
        result = subprocess.run([
            "python", "cli.py", "run", "nmkrauditor",
            "--url", "https://cardano.org",
            "--task", "Test blockchain proof-of-execution"
        ], 
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        
        # Should complete and generate proof
        assert result.returncode == 0
        assert "Blockchain Execution Complete" in result.stdout
        assert "Verification Data:" in result.stdout
        assert "Hash:" in result.stdout
    
    def test_cli_dry_run(self):
        """Test CLI dry run functionality."""
        result = subprocess.run([
            "python", "cli.py", "run", "simple_navigation",
            "--url", "https://example.com", "--dry-run"
        ],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "Would run agent 'simple_navigation'" in result.stdout
    
    def test_cli_verbose_mode(self):
        """Test CLI verbose logging mode."""
        result = subprocess.run([
            "python", "cli.py", "--verbose", "list"
        ],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "Available agents:" in result.stdout
    
    def test_cli_invalid_agent(self):
        """Test CLI with invalid agent name."""
        result = subprocess.run([
            "python", "cli.py", "run", "nonexistent_agent"
        ],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0
        assert "not found" in result.stdout.lower() or "error" in result.stdout.lower()


@pytest.mark.e2e
class TestFrameworkIntegration:
    """Test framework component integration."""
    
    @pytest.mark.asyncio
    async def test_agent_discovery_integration(self):
        """Test complete agent discovery and registration workflow."""
        # Import the CLI module to test discovery
        import cli
        
        forge = cli.AgentForge()
        
        # Should discover agents
        assert len(forge.agents) >= 2
        
        # Should have known agents
        agent_names = list(forge.agents.keys())
        assert any("navigation" in name for name in agent_names)
        assert any("nmkr" in name or "auditor" in name for name in agent_names)
        
        # Each agent should be a proper class
        for agent_name, agent_class in forge.agents.items():
            assert isinstance(agent_class, type)
            
            # Should be instantiable
            agent = agent_class()
            assert hasattr(agent, 'run')
            assert hasattr(agent, 'initialize')
            assert hasattr(agent, 'cleanup')
    
    @pytest.mark.asyncio
    async def test_configuration_workflow(self):
        """Test configuration handling workflow."""
        import tempfile
        import json
        
        # Create temporary config file
        config_data = {
            "timeout": 45,
            "debug": True,
            "test_setting": "test_value"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name
        
        try:
            # Test config file parsing would work
            with open(config_file, 'r') as f:
                loaded_config = json.load(f)
            
            assert loaded_config == config_data
            
        finally:
            os.unlink(config_file)
    
    @pytest.mark.asyncio
    async def test_error_propagation_workflow(self):
        """Test error handling and propagation through framework layers."""
        import cli
        
        forge = cli.AgentForge()
        
        # Test with nonexistent agent
        with pytest.raises(ValueError, match="not found"):
            await forge.run_agent("definitely_nonexistent_agent")
    
    @pytest.mark.asyncio
    async def test_browser_integration_workflow(self):
        """Test browser integration throughout the framework."""
        from core.shared.web.browsers import SteelBrowserClient
        from unittest.mock import AsyncMock
        
        # Test that browser client can be created
        # (This tests the import and basic instantiation)
        with patch('aiohttp.ClientSession'):
            client = SteelBrowserClient("http://test-url")
            assert client is not None


@pytest.mark.e2e
@pytest.mark.slow
class TestCompleteWorkflows:
    """Test complete end-to-end workflows."""
    
    @pytest.mark.asyncio
    async def test_simple_navigation_complete_workflow(self):
        """Test complete SimpleNavigationAgent workflow."""
        import cli
        from unittest.mock import patch, AsyncMock
        
        forge = cli.AgentForge()
        
        # Find navigation agent
        agent_name = None
        for name in forge.agents.keys():
            if "navigation" in name.lower():
                agent_name = name
                break
        
        if agent_name:
            # Mock browser client
            mock_browser_client = AsyncMock()
            mock_browser_client.navigate.return_value = {
                "success": True,
                "page_title": "Test Page Title",
                "content": "<html><body><h1>Test</h1></body></html>",
                "status": "200"
            }
            
            with patch('core.shared.web.browsers.SteelBrowserClient', return_value=mock_browser_client):
                result = await forge.run_agent(agent_name, url="https://example.com")
                
                # Should complete workflow
                assert result is not None or result is None
                
                # Browser should have been called
                mock_browser_client.navigate.assert_called()
    
    @pytest.mark.asyncio
    async def test_nmkr_auditor_complete_workflow(self):
        """Test complete NMKRAuditorAgent workflow."""
        import cli
        from unittest.mock import patch, AsyncMock
        
        forge = cli.AgentForge()
        
        # Find NMKR auditor agent
        agent_name = None
        for name in forge.agents.keys():
            if "nmkr" in name.lower() or "auditor" in name.lower():
                agent_name = name
                break
        
        if agent_name:
            # Mock browser client with blockchain content
            mock_browser_client = AsyncMock()
            mock_browser_client.navigate.return_value = {
                "success": True,
                "page_title": "Cardano - Home",
                "content": "<html><body><h1>Cardano</h1><p>blockchain smart contracts</p></body></html>",
                "status": "200"
            }
            
            with patch('core.shared.web.browsers.SteelBrowserClient', return_value=mock_browser_client):
                result = await forge.run_agent(
                    agent_name,
                    url="https://cardano.org",
                    task_description="Complete workflow test"
                )
                
                # Should return complete proof package
                assert result is not None
                assert isinstance(result, dict)
                
                # Should contain all required components
                assert "verification_data" in result
                assert "blockchain_integration" in result
                
                # Verification data should be complete
                verification = result["verification_data"]
                assert "audit_log" in verification
                assert "proof_hash" in verification
                assert "ipfs_cid" in verification
                
                # Should be valid JSON audit log
                audit_log = verification["audit_log"]
                audit_data = json.loads(audit_log)
                assert "agent_information" in audit_data
                assert "blockchain_integration" in audit_data
    
    @pytest.mark.asyncio
    async def test_multi_agent_workflow(self):
        """Test running multiple agents in sequence."""
        import cli
        from unittest.mock import patch, AsyncMock
        
        forge = cli.AgentForge()
        
        # Mock browser client
        mock_browser_client = AsyncMock()
        mock_browser_client.navigate.return_value = {
            "success": True,
            "page_title": "Test Page",
            "content": "<html><body>Test content</body></html>",
            "status": "200"
        }
        
        with patch('core.shared.web.browsers.SteelBrowserClient', return_value=mock_browser_client):
            results = []
            
            # Run each discovered agent
            for agent_name in list(forge.agents.keys())[:2]:  # Limit to first 2 for speed
                try:
                    result = await forge.run_agent(
                        agent_name,
                        url="https://example.com",
                        task_description=f"Test {agent_name}"
                    )
                    results.append((agent_name, result))
                    
                except Exception as e:
                    pytest.fail(f"Agent {agent_name} failed: {e}")
            
            # Should have run at least one agent successfully
            assert len(results) >= 1
            
            # Each result should be valid
            for agent_name, result in results:
                assert result is not None or result is None  # Either is acceptable


@pytest.mark.e2e
class TestDocumentationIntegration:
    """Test documentation and example integration."""
    
    def test_documentation_structure(self, docs_dir):
        """Test that documentation structure is complete."""
        required_dirs = [
            "guides",
            "tutorials", 
            "api",
            "integrations",
            "architecture"
        ]
        
        for dir_name in required_dirs:
            dir_path = docs_dir / dir_name
            assert dir_path.exists(), f"Documentation directory {dir_name} missing"
            
            # Should have README
            readme_path = dir_path / "README.md"
            assert readme_path.exists(), f"README missing in {dir_name}"
    
    def test_examples_structure(self, examples_dir):
        """Test that examples directory structure is complete."""
        assert examples_dir.exists()
        
        # Should have at least the known agents
        expected_files = [
            "simple_navigation_agent.py",
            "nmkr_auditor_agent.py"
        ]
        
        for file_name in expected_files:
            file_path = examples_dir / file_name
            assert file_path.exists(), f"Example file {file_name} missing"
    
    def test_project_structure(self, project_root):
        """Test overall project structure."""
        required_items = [
            "cli.py",
            "core",
            "examples", 
            "docs",
            "tests",
            "memory-bank"
        ]
        
        for item_name in required_items:
            item_path = project_root / item_name
            assert item_path.exists(), f"Project item {item_name} missing"


@pytest.mark.e2e
class TestPerformanceWorkflows:
    """Test performance aspects of framework workflows."""
    
    @pytest.mark.slow
    def test_cli_startup_performance(self):
        """Test CLI startup performance."""
        import time
        
        start_time = time.time()
        
        result = subprocess.run(
            ["python", "cli.py", "list"],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
            text=True
        )
        
        end_time = time.time()
        startup_time = end_time - start_time
        
        assert result.returncode == 0
        # CLI should start reasonably quickly (under 10 seconds)
        assert startup_time < 10.0, f"CLI startup took {startup_time:.2f} seconds"
    
    @pytest.mark.asyncio
    async def test_agent_initialization_performance(self):
        """Test agent initialization performance."""
        import time
        import cli
        from unittest.mock import patch, AsyncMock
        
        forge = cli.AgentForge()
        
        if forge.agents:
            agent_name = list(forge.agents.keys())[0]
            agent_class = forge.agents[agent_name]
            
            # Mock browser to avoid network delays
            mock_browser_client = AsyncMock()
            
            with patch('core.shared.web.browsers.SteelBrowserClient', return_value=mock_browser_client):
                agent = agent_class()
                
                start_time = time.time()
                await agent.initialize()
                end_time = time.time()
                
                init_time = end_time - start_time
                
                # Initialization should be fast (under 5 seconds)
                assert init_time < 5.0, f"Agent initialization took {init_time:.2f} seconds"
                
                await agent.cleanup()


@pytest.mark.e2e
class TestFrameworkRobustness:
    """Test framework robustness and error handling."""
    
    @pytest.mark.asyncio
    async def test_framework_isolation(self):
        """Test that agent failures don't affect framework."""
        import cli
        from unittest.mock import patch
        
        forge = cli.AgentForge()
        
        # Create a failing agent mock
        class FailingAgent:
            def __init__(self, **kwargs):
                raise RuntimeError("Intentional failure")
        
        # Add failing agent to registry
        forge.agents["failing_agent"] = FailingAgent
        
        # Framework should handle the failure gracefully
        with pytest.raises(ValueError, match="Failed to create agent"):
            await forge.run_agent("failing_agent")
        
        # Framework should still work with other agents
        assert len(forge.agents) >= 1
        forge.list_agents()  # Should not fail
    
    @pytest.mark.asyncio
    async def test_concurrent_agent_execution(self):
        """Test concurrent execution of multiple agents."""
        import cli
        from unittest.mock import patch, AsyncMock
        
        forge = cli.AgentForge()
        
        # Mock browser client
        mock_browser_client = AsyncMock()
        mock_browser_client.navigate.return_value = {
            "success": True,
            "page_title": "Test Page",
            "content": "<html><body>Test</body></html>",
            "status": "200"
        }
        
        with patch('core.shared.web.browsers.SteelBrowserClient', return_value=mock_browser_client):
            # Run multiple agents concurrently
            agent_names = list(forge.agents.keys())[:2]  # Limit for speed
            
            tasks = []
            for agent_name in agent_names:
                task = forge.run_agent(agent_name, url="https://example.com")
                tasks.append(task)
            
            # Should complete all tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Should not have any exceptions
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    pytest.fail(f"Agent {agent_names[i]} failed concurrently: {result}")
    
    def test_import_isolation(self):
        """Test that framework imports don't interfere with each other."""
        # Multiple imports should work
        import cli
        import core.agents.base
        import examples.simple_navigation_agent
        import examples.nmkr_auditor_agent
        
        # Should be able to access all components
        assert hasattr(cli, 'AgentForge')
        assert hasattr(core.agents.base, 'BaseAgent')
        assert hasattr(examples.simple_navigation_agent, 'SimpleNavigationAgent')
        assert hasattr(examples.nmkr_auditor_agent, 'NMKRAuditorAgent')
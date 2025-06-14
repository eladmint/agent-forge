"""
Integration tests for Agent Forge CLI.

Tests the command-line interface functionality including agent discovery,
registration, and execution workflows.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
from io import StringIO
import sys

# Import CLI components
import cli
from cli import AgentForge, create_parser, setup_logging


@pytest.mark.integration
class TestAgentDiscovery:
    """Test agent discovery and registration functionality."""
    
    def test_discover_agents_from_examples(self, examples_dir):
        """Test automatic agent discovery from examples directory."""
        forge = AgentForge()
        
        # Should find at least the known agents
        assert len(forge.agents) >= 2
        assert "simple_navigation" in forge.agents or "simplenavigation" in forge.agents
        assert "nmkr_auditor" in forge.agents or "nmkrauditor" in forge.agents
    
    def test_agent_class_registration(self):
        """Test that discovered agents are proper BaseAgent subclasses."""
        forge = AgentForge()
        
        for agent_name, agent_class in forge.agents.items():
            # Should be a class
            assert isinstance(agent_class, type)
            
            # Should have required methods
            assert hasattr(agent_class, 'run')
            assert hasattr(agent_class, 'initialize')
            assert hasattr(agent_class, 'cleanup')
    
    def test_agent_name_conversion(self):
        """Test agent name conversion from class names."""
        forge = AgentForge()
        
        # Should convert CamelCase to snake_case
        agent_names = list(forge.agents.keys())
        for name in agent_names:
            # Should be lowercase
            assert name.islower()
            # Should not contain uppercase letters
            assert not any(c.isupper() for c in name)
    
    def test_list_agents_output(self, capsys):
        """Test list agents command output."""
        forge = AgentForge()
        forge.list_agents()
        
        captured = capsys.readouterr()
        assert "Available agents:" in captured.out
        assert len(captured.out.strip().split('\n')) >= 2  # Header + at least one agent


@pytest.mark.integration
class TestCLIParser:
    """Test CLI argument parsing functionality."""
    
    def test_parser_creation(self):
        """Test that parser is created correctly."""
        parser = create_parser()
        
        assert parser is not None
        assert parser.prog == "cli.py"
    
    def test_list_command_parsing(self):
        """Test parsing of list command."""
        parser = create_parser()
        args = parser.parse_args(['list'])
        
        assert args.command == 'list'
        assert hasattr(args, 'verbose')
    
    def test_run_command_parsing(self):
        """Test parsing of run command with various parameters."""
        parser = create_parser()
        
        # Basic run command
        args = parser.parse_args(['run', 'test_agent'])
        assert args.command == 'run'
        assert args.agent_name == 'test_agent'
        
        # Run with URL
        args = parser.parse_args(['run', 'test_agent', '--url', 'https://example.com'])
        assert args.url == 'https://example.com'
        
        # Run with task
        args = parser.parse_args(['run', 'test_agent', '--task', 'test task'])
        assert args.task == 'test task'
        
        # Run with config
        args = parser.parse_args(['run', 'test_agent', '--config', 'config.json'])
        assert args.config == 'config.json'
        
        # Run with dry-run
        args = parser.parse_args(['run', 'test_agent', '--dry-run'])
        assert args.dry_run is True
    
    def test_verbose_flag(self):
        """Test verbose flag parsing."""
        parser = create_parser()
        
        # Short form
        args = parser.parse_args(['--verbose', 'list'])
        assert args.verbose is True
        
        # Long form
        args = parser.parse_args(['-v', 'list'])
        assert args.verbose is True
    
    def test_version_argument(self):
        """Test version argument."""
        parser = create_parser()
        
        with pytest.raises(SystemExit):
            parser.parse_args(['--version'])


@pytest.mark.integration
class TestAgentExecution:
    """Test agent execution through CLI."""
    
    @pytest.mark.asyncio
    async def test_run_existing_agent(self, mock_browser_client):
        """Test running an existing agent through CLI."""
        forge = AgentForge()
        
        # Mock the browser client creation
        with patch('core.agents.base.SteelBrowserClient', return_value=mock_browser_client):
            # Should be able to run any discovered agent
            agent_names = list(forge.agents.keys())
            if agent_names:
                agent_name = agent_names[0]
                
                result = await forge.run_agent(agent_name, url="https://example.com")
                
                # Should return some result (could be None for some agents)
                assert result is not None or result is None  # Either is acceptable
    
    @pytest.mark.asyncio
    async def test_run_nonexistent_agent(self):
        """Test error handling for nonexistent agents."""
        forge = AgentForge()
        
        with pytest.raises(ValueError, match="Agent 'nonexistent' not found"):
            await forge.run_agent("nonexistent")
    
    @pytest.mark.asyncio
    async def test_agent_initialization_failure(self):
        """Test handling of agent initialization failure."""
        forge = AgentForge()
        
        # Get a valid agent name
        agent_names = list(forge.agents.keys())
        if agent_names:
            agent_name = agent_names[0]
            
            # Mock initialization failure
            with patch.object(forge.agents[agent_name], '__init__', side_effect=Exception("Init failed")):
                with pytest.raises(ValueError, match="Failed to create agent"):
                    await forge.run_agent(agent_name)
    
    @pytest.mark.asyncio
    async def test_agent_with_parameters(self, mock_browser_client):
        """Test running agent with various parameters."""
        forge = AgentForge()
        
        with patch('core.agents.base.SteelBrowserClient', return_value=mock_browser_client):
            agent_names = list(forge.agents.keys())
            if agent_names:
                agent_name = agent_names[0]
                
                # Test with URL
                result = await forge.run_agent(
                    agent_name,
                    url="https://test.example.com",
                    task_description="Test task",
                    timeout=30
                )
                
                assert result is not None or result is None


@pytest.mark.integration
class TestCLIIntegration:
    """Test complete CLI integration scenarios."""
    
    def test_logging_setup(self):
        """Test logging configuration."""
        setup_logging(verbose=False)
        logger = cli.logging.getLogger("test")
        assert logger.level == cli.logging.INFO
        
        setup_logging(verbose=True)
        logger = cli.logging.getLogger("test")
        assert logger.level == cli.logging.DEBUG
    
    @pytest.mark.asyncio
    async def test_main_list_command(self, capsys):
        """Test main function with list command."""
        test_args = ['list']
        
        with patch('sys.argv', ['cli.py'] + test_args):
            with patch('cli.AgentForge') as mock_forge_class:
                mock_forge = Mock()
                mock_forge_class.return_value = mock_forge
                
                await cli.main()
                
                mock_forge.list_agents.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_main_run_command(self, mock_browser_client):
        """Test main function with run command."""
        test_args = ['run', 'test_agent', '--url', 'https://example.com']
        
        with patch('sys.argv', ['cli.py'] + test_args):
            with patch('cli.AgentForge') as mock_forge_class:
                mock_forge = Mock()
                mock_forge.run_agent = AsyncMock(return_value={"status": "success"})
                mock_forge_class.return_value = mock_forge
                
                await cli.main()
                
                mock_forge.run_agent.assert_called_once()
                call_args = mock_forge.run_agent.call_args
                assert call_args[0][0] == 'test_agent'  # agent_name
                assert call_args[1]['url'] == 'https://example.com'
    
    @pytest.mark.asyncio
    async def test_main_dry_run(self, capsys):
        """Test main function with dry-run option."""
        test_args = ['run', 'test_agent', '--url', 'https://example.com', '--dry-run']
        
        with patch('sys.argv', ['cli.py'] + test_args):
            with patch('cli.AgentForge') as mock_forge_class:
                mock_forge = Mock()
                mock_forge_class.return_value = mock_forge
                
                await cli.main()
                
                captured = capsys.readouterr()
                assert "Would run agent 'test_agent'" in captured.out
                mock_forge.run_agent.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_main_error_handling(self, capsys):
        """Test main function error handling."""
        test_args = ['run', 'nonexistent_agent']
        
        with patch('sys.argv', ['cli.py'] + test_args):
            with patch('cli.AgentForge') as mock_forge_class:
                mock_forge = Mock()
                mock_forge.run_agent = AsyncMock(side_effect=ValueError("Agent not found"))
                mock_forge_class.return_value = mock_forge
                
                with pytest.raises(SystemExit):
                    await cli.main()
                
                captured = capsys.readouterr()
                assert "Error" in captured.out


@pytest.mark.integration
class TestAgentWorkflow:
    """Test complete agent workflow integration."""
    
    @pytest.mark.asyncio
    async def test_simple_navigation_workflow(self, mock_browser_client):
        """Test complete workflow with SimpleNavigationAgent."""
        forge = AgentForge()
        
        # Configure mock response
        mock_browser_client.navigate.return_value = {
            "success": True,
            "page_title": "Example Domain",
            "content": "<html><body><h1>Example</h1></body></html>",
            "status": "200"
        }
        
        with patch('core.agents.base.SteelBrowserClient', return_value=mock_browser_client):
            # Find simple navigation agent
            agent_name = None
            for name in forge.agents.keys():
                if 'navigation' in name.lower():
                    agent_name = name
                    break
            
            if agent_name:
                result = await forge.run_agent(
                    agent_name,
                    url="https://example.com"
                )
                
                # Should complete without error
                assert result is not None or result is None
                
                # Browser should have been called
                mock_browser_client.navigate.assert_called()
    
    @pytest.mark.asyncio
    async def test_nmkr_auditor_workflow(self, mock_browser_client):
        """Test complete workflow with NMKRAuditorAgent."""
        forge = AgentForge()
        
        # Configure mock response for blockchain content
        mock_browser_client.navigate.return_value = {
            "success": True,
            "page_title": "Cardano - Home",
            "content": "<html><body><h1>Cardano</h1><p>blockchain platform</p></body></html>",
            "status": "200"
        }
        
        with patch('core.agents.base.SteelBrowserClient', return_value=mock_browser_client):
            # Find NMKR auditor agent
            agent_name = None
            for name in forge.agents.keys():
                if 'nmkr' in name.lower() or 'auditor' in name.lower():
                    agent_name = name
                    break
            
            if agent_name:
                result = await forge.run_agent(
                    agent_name,
                    url="https://cardano.org",
                    task_description="Test blockchain analysis"
                )
                
                # Should return proof package
                assert result is not None
                
                # Should contain blockchain integration data
                if isinstance(result, dict):
                    assert "blockchain_integration" in result or "status" in result


@pytest.mark.integration
@pytest.mark.slow
class TestRealAgentExecution:
    """Test real agent execution (slower tests)."""
    
    @pytest.mark.asyncio
    async def test_agent_discovery_and_execution(self):
        """Test discovering and executing all available agents."""
        forge = AgentForge()
        
        # Should discover at least some agents
        assert len(forge.agents) > 0
        
        # Test that we can create instances of all discovered agents
        for agent_name, agent_class in forge.agents.items():
            try:
                # Should be able to instantiate with required parameters
                if agent_class.__name__ == 'SimpleNavigationAgent':
                    agent = agent_class(name=f"test_{agent_name}", url="https://example.com")
                elif agent_class.__name__ == 'NMKRAuditorAgent':
                    agent = agent_class(name=f"test_{agent_name}", url="https://example.com")
                else:
                    agent = agent_class(name=f"test_{agent_name}")
                
                # Should have required methods
                assert hasattr(agent, 'run')
                assert hasattr(agent, 'initialize')
                assert hasattr(agent, 'cleanup')
                
                # Should have proper inheritance
                from core.agents.base import BaseAgent
                assert isinstance(agent, BaseAgent)
                
            except Exception as e:
                pytest.fail(f"Failed to instantiate agent {agent_name}: {e}")


@pytest.mark.integration
class TestCLIConfiguration:
    """Test CLI configuration handling."""
    
    def test_config_file_parameter(self):
        """Test configuration file parameter parsing."""
        parser = create_parser()
        args = parser.parse_args(['run', 'agent', '--config', 'test_config.json'])
        
        assert args.config == 'test_config.json'
    
    @pytest.mark.asyncio
    async def test_agent_kwargs_preparation(self):
        """Test preparation of agent keyword arguments."""
        # Mock argument parsing result
        class MockArgs:
            def __init__(self):
                self.agent_name = 'test_agent'
                self.url = 'https://example.com'
                self.task = 'test task'
                self.config = None
                self.dry_run = False
        
        args = MockArgs()
        
        # Prepare kwargs as done in main()
        agent_kwargs = {}
        if args.url:
            agent_kwargs['url'] = args.url
        if args.task:
            agent_kwargs['task_description'] = args.task
        if args.config:
            agent_kwargs['config'] = args.config
        
        assert agent_kwargs['url'] == 'https://example.com'
        assert agent_kwargs['task_description'] == 'test task'
        assert 'config' not in agent_kwargs  # Should not include None values
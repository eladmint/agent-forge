#!/usr/bin/env python3
"""
Claude Desktop Integration Test Scenarios

Real-world test scenarios for validating Agent Forge MCP integration
in Claude Desktop with practical use cases and conversational commands.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List
import unittest

# Add current directory to Python path
current_dir = Path(__file__).parent.parent.parent  # Go up to agent_forge root
sys.path.insert(0, str(current_dir))

class ClaudeDesktopScenarioTests(unittest.TestCase):
    """Test scenarios that simulate real Claude Desktop usage."""
    
    def setUp(self):
        """Set up test scenarios."""
        self.test_scenarios = self._load_test_scenarios()
    
    def _load_test_scenarios(self) -> List[Dict[str, Any]]:
        """Load comprehensive test scenarios for Claude Desktop."""
        return [
            {
                "name": "Basic Agent Info Query",
                "description": "User wants to see available Agent Forge capabilities",
                "user_command": "Claude, use get_agent_info to show me all available Agent Forge tools and their capabilities",
                "expected_tool": "get_agent_info",
                "expected_response_elements": [
                    "Agent Forge", "framework", "total_agents", "SimpleNavigationAgent", 
                    "NMKRAuditorAgent", "blockchain_integration", "steel_browser"
                ],
                "difficulty": "beginner",
                "category": "information"
            },
            {
                "name": "Website Navigation Request",
                "description": "User wants to navigate and extract content from a website",
                "user_command": "Use navigate_website to visit TechCrunch and extract the top 3 headlines from the homepage",
                "expected_tool": "navigate_website",
                "expected_parameters": {
                    "url": "https://techcrunch.com",
                    "extraction_target": "content"
                },
                "expected_response_elements": [
                    "success", "page_title", "extracted_content", "SimpleNavigationAgent"
                ],
                "difficulty": "intermediate",
                "category": "web_automation"
            },
            {
                "name": "Blockchain Proof Generation",
                "description": "User wants to create a blockchain proof for verification",
                "user_command": "Generate a blockchain proof for my comprehensive analysis of Apple's homepage accessibility and performance",
                "expected_tool": "generate_blockchain_proof",
                "expected_parameters": {
                    "task_description": "comprehensive analysis of Apple's homepage accessibility and performance"
                },
                "expected_response_elements": [
                    "success", "nft_metadata", "proof_hash", "ipfs_cid", "NMKRAuditorAgent"
                ],
                "difficulty": "advanced",
                "category": "blockchain"
            },
            {
                "name": "Multi-Source Data Compilation",
                "description": "User wants to compile data from multiple sources",
                "user_command": "Use compile_data_from_sources to gather pricing information from these 3 competitor websites and create a comparison table",
                "expected_tool": "compile_data_from_sources",
                "expected_parameters": {
                    "sources": ["competitor1.com", "competitor2.com", "competitor3.com"],
                    "instructions": "gather pricing information and create a comparison table"
                },
                "expected_response_elements": [
                    "success", "compiled_data", "source_summaries", "DataCompilerAgent"
                ],
                "difficulty": "intermediate", 
                "category": "data_analysis"
            },
            {
                "name": "Content Extraction Request",
                "description": "User wants to extract clean content from an article",
                "user_command": "Use extract_text_content to get the full article text from this research paper URL and format it as clean markdown",
                "expected_tool": "extract_text_content",
                "expected_parameters": {
                    "url": "https://arxiv.org/abs/2024.12345",
                    "content_type": "article",
                    "include_metadata": True
                },
                "expected_response_elements": [
                    "success", "content", "EnhancedTextExtractionAgent"
                ],
                "difficulty": "intermediate",
                "category": "content_processing"
            },
            {
                "name": "Website Validation Request",
                "description": "User wants to validate website for accessibility issues",
                "user_command": "Run validate_website_data on our company website to check for accessibility issues and provide improvement recommendations",
                "expected_tool": "validate_website_data",
                "expected_parameters": {
                    "url": "company_website_url",
                    "check_accessibility": True
                },
                "expected_response_elements": [
                    "success", "validation_results", "EnhancedValidationAgent"
                ],
                "difficulty": "intermediate",
                "category": "validation"
            },
            {
                "name": "Complex Multi-Tool Workflow",
                "description": "User wants to use multiple tools in sequence",
                "user_command": "First use navigate_website to analyze Tesla.com homepage, then validate_website_data to check for issues, and finally generate_blockchain_proof to create a verification record",
                "expected_tools": ["navigate_website", "validate_website_data", "generate_blockchain_proof"],
                "expected_workflow": "sequential",
                "difficulty": "advanced",
                "category": "workflow"
            },
            {
                "name": "Natural Language Ambiguous Request",
                "description": "User makes a vague request that needs interpretation",
                "user_command": "Help me research my competitors and create a report",
                "expected_interpretation": "Could use compile_data_from_sources or navigate_website",
                "requires_clarification": True,
                "difficulty": "advanced",
                "category": "interpretation"
            },
            {
                "name": "Error Recovery Scenario", 
                "description": "User provides invalid URL or parameters",
                "user_command": "Use navigate_website to visit not-a-real-website-url-123.com",
                "expected_tool": "navigate_website",
                "expected_error_handling": True,
                "expected_response_elements": [
                    ("success", False), ("error", True), ("message", "invalid URL")
                ],
                "difficulty": "intermediate",
                "category": "error_handling"
            },
            {
                "name": "Performance Intensive Request",
                "description": "User requests processing of multiple large sources",
                "user_command": "Use the data_compiler agent to analyze these 10 market research reports and identify common trends",
                "expected_tool": "data_compiler",
                "performance_considerations": True,
                "expected_timeout": 60,
                "difficulty": "advanced",
                "category": "performance"
            }
        ]
    
    def test_scenario_coverage(self):
        """Test that all important scenarios are covered."""
        print("\n📋 Testing Scenario Coverage...")
        
        categories = set(scenario['category'] for scenario in self.test_scenarios)
        difficulties = set(scenario['difficulty'] for scenario in self.test_scenarios)
        tools_covered = set()
        
        for scenario in self.test_scenarios:
            if 'expected_tool' in scenario:
                tools_covered.add(scenario['expected_tool'])
            if 'expected_tools' in scenario:
                tools_covered.update(scenario['expected_tools'])
        
        expected_categories = {
            'information', 'web_automation', 'blockchain', 'data_analysis',
            'content_processing', 'validation', 'workflow', 'interpretation',
            'error_handling', 'performance'
        }
        
        expected_tools = {
            'navigate_website', 'generate_blockchain_proof', 'compile_data_from_sources',
            'extract_text_content', 'validate_website_data', 'get_agent_info'
        }
        
        self.assertEqual(categories, expected_categories, "Missing test categories")
        self.assertEqual(tools_covered, expected_tools, "Not all tools covered in scenarios")
        
        print(f"   ✅ Categories covered: {len(categories)}")
        print(f"   ✅ Tools covered: {len(tools_covered)}")
        print(f"   ✅ Total scenarios: {len(self.test_scenarios)}")
    
    def test_scenario_structure_validation(self):
        """Validate that all scenarios have proper structure."""
        print("\n🔍 Testing Scenario Structure...")
        
        required_fields = ['name', 'description', 'user_command', 'difficulty', 'category']
        
        for i, scenario in enumerate(self.test_scenarios):
            with self.subTest(scenario=scenario['name']):
                for field in required_fields:
                    self.assertIn(field, scenario, f"Scenario {i+1} missing field: {field}")
                
                # Validate difficulty levels
                self.assertIn(scenario['difficulty'], ['beginner', 'intermediate', 'advanced'])
                
                # Validate command is meaningful
                self.assertGreater(len(scenario['user_command']), 20, "Command too short")
                
        print(f"   ✅ All {len(self.test_scenarios)} scenarios properly structured")
    
    def test_conversational_command_patterns(self):
        """Test that commands follow natural conversational patterns."""
        print("\n💬 Testing Conversational Command Patterns...")
        
        natural_patterns = [
            "use ", "help me", "please", "can you", "i want to", "i need"
        ]
        
        conversational_commands = 0
        
        for scenario in self.test_scenarios:
            command = scenario['user_command'].lower()
            if any(pattern in command for pattern in natural_patterns):
                conversational_commands += 1
        
        # At least 80% of commands should be conversational
        conversational_ratio = conversational_commands / len(self.test_scenarios)
        self.assertGreater(conversational_ratio, 0.8, "Commands should be more conversational")
        
        print(f"   ✅ Conversational commands: {conversational_ratio:.1%}")
    
    def test_tool_parameter_extraction(self):
        """Test that expected parameters can be extracted from commands."""
        print("\n🔧 Testing Tool Parameter Extraction...")
        
        for scenario in self.test_scenarios:
            if 'expected_parameters' not in scenario:
                continue
                
            with self.subTest(scenario=scenario['name']):
                command = scenario['user_command']
                expected_params = scenario['expected_parameters']
                
                # Test URL extraction
                if 'url' in expected_params:
                    # URL should be extractable from command context
                    self.assertTrue(
                        'techcrunch' in command.lower() or 
                        'apple' in command.lower() or
                        'website' in command.lower() or
                        'http' in command.lower(),
                        f"URL context not clear in command: {command}"
                    )
                
                # Test instruction extraction
                if 'instructions' in expected_params:
                    instruction_keywords = ['gather', 'extract', 'analyze', 'compare', 'create']
                    self.assertTrue(
                        any(keyword in command.lower() for keyword in instruction_keywords),
                        f"Instructions not clear in command: {command}"
                    )
        
        print("   ✅ Parameter extraction patterns validated")
    
    def test_error_scenario_coverage(self):
        """Test that error scenarios are properly covered."""
        print("\n🛡️ Testing Error Scenario Coverage...")
        
        error_scenarios = [s for s in self.test_scenarios if s.get('expected_error_handling')]
        self.assertGreater(len(error_scenarios), 0, "No error scenarios defined")
        
        error_types_covered = set()
        for scenario in error_scenarios:
            if 'invalid URL' in str(scenario.get('expected_response_elements', [])):
                error_types_covered.add('invalid_url')
            if scenario.get('requires_clarification'):
                error_types_covered.add('ambiguous_request')
        
        print(f"   ✅ Error scenarios: {len(error_scenarios)}")
        print(f"   ✅ Error types covered: {len(error_types_covered)}")
    
    def test_performance_scenario_coverage(self):
        """Test that performance scenarios are included."""
        print("\n⚡ Testing Performance Scenario Coverage...")
        
        performance_scenarios = [s for s in self.test_scenarios if s.get('performance_considerations')]
        self.assertGreater(len(performance_scenarios), 0, "No performance scenarios defined")
        
        for scenario in performance_scenarios:
            if 'expected_timeout' in scenario:
                self.assertGreater(scenario['expected_timeout'], 30, "Timeout should be realistic")
        
        print(f"   ✅ Performance scenarios: {len(performance_scenarios)}")


class ClaudeDesktopConfigurationTests(unittest.TestCase):
    """Test Claude Desktop configuration scenarios."""
    
    def test_config_file_variations(self):
        """Test different Claude Desktop configuration variations."""
        print("\n⚙️ Testing Configuration Variations...")
        
        base_config = {
            "mcpServers": {
                "agent-forge": {
                    "command": "python",
                    "args": ["/Users/eladm/Projects/token/tokenhunter/agent_forge/mcp_server.py"],
                    "env": {
                        "PYTHONPATH": "/Users/eladm/Projects/token/tokenhunter/agent_forge"
                    }
                }
            }
        }
        
        # Test basic config
        self.assertIn('mcpServers', base_config)
        print("   ✅ Basic configuration structure valid")
        
        # Test virtual environment config
        venv_config = base_config.copy()
        venv_config['mcpServers']['agent-forge']['command'] = "/path/to/venv/bin/python"
        self.assertIn('venv', venv_config['mcpServers']['agent-forge']['command'])
        print("   ✅ Virtual environment configuration valid")
        
        # Test with environment variables
        env_config = base_config.copy()
        env_config['mcpServers']['agent-forge']['env'].update({
            "NMKR_API_KEY": "your-api-key",
            "LOG_LEVEL": "DEBUG"
        })
        self.assertEqual(len(env_config['mcpServers']['agent-forge']['env']), 3)
        print("   ✅ Environment variables configuration valid")
    
    def test_cross_platform_configs(self):
        """Test configuration for different platforms."""
        print("\n🌐 Testing Cross-Platform Configurations...")
        
        platforms = {
            'macOS': '~/Library/Application Support/Claude/claude_desktop_config.json',
            'Windows': '%APPDATA%/Claude/claude_desktop_config.json',
            'Linux': '~/.config/Claude/claude_desktop_config.json'
        }
        
        for platform, config_path in platforms.items():
            self.assertIn('Claude', config_path)
            self.assertTrue(config_path.endswith('.json'))
            print(f"   ✅ {platform} config path valid: {config_path}")


def generate_test_scenarios_documentation():
    """Generate documentation for test scenarios."""
    print("\n📚 Generating Test Scenarios Documentation...")
    
    tests = ClaudeDesktopScenarioTests()
    tests.setUp()
    scenarios = tests.test_scenarios
    
    doc_content = """# Claude Desktop Test Scenarios

This document contains comprehensive test scenarios for validating Agent Forge MCP integration with Claude Desktop.

## Test Scenario Categories

"""
    
    # Group by category
    categories = {}
    for scenario in scenarios:
        category = scenario['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(scenario)
    
    for category, category_scenarios in categories.items():
        doc_content += f"\n### {category.replace('_', ' ').title()}\n\n"
        
        for scenario in category_scenarios:
            doc_content += f"#### {scenario['name']} ({scenario['difficulty']})\n"
            doc_content += f"**Description:** {scenario['description']}\n\n"
            doc_content += f"**User Command:**\n```\n{scenario['user_command']}\n```\n\n"
            
            if 'expected_tool' in scenario:
                doc_content += f"**Expected Tool:** `{scenario['expected_tool']}`\n\n"
            
            if 'expected_parameters' in scenario:
                doc_content += f"**Expected Parameters:**\n```json\n{json.dumps(scenario['expected_parameters'], indent=2)}\n```\n\n"
            
            doc_content += "---\n\n"
    
    doc_content += """
## Usage Instructions

1. **Setup Claude Desktop** with Agent Forge MCP configuration
2. **Test each scenario** by copying the user command into Claude Desktop
3. **Verify responses** match expected tools and response elements
4. **Check error handling** for scenarios marked with error handling
5. **Monitor performance** for scenarios with performance considerations

## Success Criteria

- ✅ All tools respond correctly to natural language commands
- ✅ Parameters are extracted accurately from conversational input
- ✅ Error scenarios are handled gracefully
- ✅ Performance scenarios complete within expected timeframes
- ✅ Multi-tool workflows execute in proper sequence
"""
    
    # Write documentation
    doc_path = current_dir / "tests" / "claude_desktop_test_scenarios.md"
    with open(doc_path, 'w') as f:
        f.write(doc_content)
    
    print(f"   ✅ Documentation generated: {doc_path}")
    return doc_path


if __name__ == '__main__':
    print("🧪 Claude Desktop Integration Test Scenarios")
    print("=" * 50)
    
    # Run tests
    unittest.main(verbosity=2, exit=False)
    
    # Generate documentation
    generate_test_scenarios_documentation()
    
    print("\n🎯 Test scenarios ready for Claude Desktop validation!")
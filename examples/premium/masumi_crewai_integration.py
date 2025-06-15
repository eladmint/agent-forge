"""
Masumi CrewAI Integration Example

This example demonstrates how to integrate Agent Forge agents with 
Masumi's CrewAI quickstart template for multi-agent workflows.

Based on: https://github.com/masumi-network/crewai-masumi-quickstart-template
"""

import asyncio
import json
from typing import Dict, Any, List
from dataclasses import dataclass

from core.shared.masumi import MasumiBridgeAdapter, MasumiConfig
from examples.simple_navigation_agent import SimpleNavigationAgent
from examples.data_compiler_agent import DataCompilerAgent


@dataclass
class CrewAITask:
    """Represents a task in CrewAI workflow."""
    description: str
    agent_type: str
    expected_output: str
    tools: List[str]
    context: Dict[str, Any] = None


# Import framework BaseAgent
from core.agents.base import AsyncContextAgent

@dataclass 
class CrewAIAgent(AsyncContextAgent):
    """CrewAI agent definition compatible with Masumi."""
    role: str
    goal: str
    backstory: str
    tools: List[str]
    verbose: bool = True
    memory: bool = False


class MasumiCrewAIAdapter:
    """Adapter that bridges Agent Forge agents to CrewAI workflows via Masumi."""
    
    def __init__(self, config: MasumiConfig = None):
        self.config = config or MasumiConfig.for_testing()
        self.bridge = MasumiBridgeAdapter(self.config)
        self.agents = {}
        self.tasks = []
        
    def add_agent_forge_agent(
        self,
        name: str,
        agent_forge_agent,
        crewai_role: str,
        crewai_goal: str,
        crewai_backstory: str,
        price_ada: float = 5.0
    ):
        """Add an Agent Forge agent to the CrewAI workflow."""
        
        # Wrap the Agent Forge agent for Masumi
        wrapped_agent = self.bridge.wrap_agent(
            agent=agent_forge_agent,
            agent_did=f"did:cardano:crewai_{name}",
            price_ada=price_ada
        )
        
        # Create CrewAI-compatible agent definition
        crewai_agent = CrewAIAgent(
            role=crewai_role,
            goal=crewai_goal,
            backstory=crewai_backstory,
            tools=wrapped_agent.get_capabilities(),
            verbose=True,
            memory=False
        )
        
        self.agents[name] = {
            'wrapped_agent': wrapped_agent,
            'crewai_agent': crewai_agent,
            'agent_forge_agent': agent_forge_agent
        }
        
        print(f"🤖 Added Agent Forge agent '{name}' to CrewAI workflow")
        print(f"   Role: {crewai_role}")
        print(f"   Price: {price_ada} ADA")
        print(f"   DID: {wrapped_agent.agent_did}")
    
    def add_task(
        self,
        description: str,
        agent_name: str,
        expected_output: str,
        context: Dict[str, Any] = None
    ):
        """Add a task to the CrewAI workflow."""
        
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not found. Add agent first.")
        
        agent_info = self.agents[agent_name]
        
        task = CrewAITask(
            description=description,
            agent_type=agent_name,
            expected_output=expected_output,
            tools=agent_info['wrapped_agent'].get_capabilities(),
            context=context or {}
        )
        
        self.tasks.append(task)
        print(f"📋 Added task: {description[:50]}...")
    
    async def execute_workflow(self, workflow_name: str = "masumi_workflow") -> Dict[str, Any]:
        """Execute the complete CrewAI workflow with Masumi payment integration."""
        
        print(f"🚀 Executing CrewAI workflow: {workflow_name}")
        print(f"📊 {len(self.agents)} agents, {len(self.tasks)} tasks")
        
        workflow_id = f"workflow_{int(asyncio.get_event_loop().time())}"
        results = {
            'workflow_id': workflow_id,
            'workflow_name': workflow_name,
            'task_results': [],
            'total_cost_ada': 0.0,
            'execution_time': 0.0,
            'success': True
        }
        
        start_time = asyncio.get_event_loop().time()
        
        # Execute tasks sequentially (CrewAI style)
        for i, task in enumerate(self.tasks):
            print(f"\n⚡ Executing Task {i+1}/{len(self.tasks)}")
            print(f"   Description: {task.description}")
            print(f"   Agent: {task.agent_type}")
            
            try:
                agent_info = self.agents[task.agent_type]
                wrapped_agent = agent_info['wrapped_agent']
                
                # Generate unique job ID for this task
                job_id = f"{workflow_id}_task_{i+1}"
                
                # Execute with Masumi integration
                task_result = await wrapped_agent.execute_with_masumi(
                    job_id=job_id,
                    # In real scenario, payment_proof would be provided
                    payment_proof=f"simulated_payment_{job_id}",
                    requester_did=f"did:cardano:crewai_workflow_{workflow_id}",
                    **task.context
                )
                
                # Add to workflow results
                results['task_results'].append({
                    'task_id': i + 1,
                    'description': task.description,
                    'agent': task.agent_type,
                    'result': task_result['result'],
                    'proof_hash': task_result['proof_hash'],
                    'cost_ada': wrapped_agent.price_ada,
                    'execution_time': task_result['execution_time'],
                    'success': True
                })
                
                results['total_cost_ada'] += wrapped_agent.price_ada
                
                print(f"   ✅ Task completed in {task_result['execution_time']:.2f}s")
                print(f"   💰 Cost: {wrapped_agent.price_ada} ADA")
                
            except Exception as e:
                print(f"   ❌ Task failed: {e}")
                
                results['task_results'].append({
                    'task_id': i + 1,
                    'description': task.description,
                    'agent': task.agent_type,
                    'error': str(e),
                    'success': False
                })
                
                results['success'] = False
        
        results['execution_time'] = asyncio.get_event_loop().time() - start_time
        
        print(f"\n🎯 Workflow completed!")
        print(f"   Total cost: {results['total_cost_ada']} ADA")
        print(f"   Execution time: {results['execution_time']:.2f}s")
        print(f"   Success rate: {sum(1 for r in results['task_results'] if r.get('success', False))}/{len(results['task_results'])}")
        
        return results
    
    def export_crewai_config(self) -> Dict[str, Any]:
        """Export configuration compatible with CrewAI format."""
        
        crewai_config = {
            'agents': {},
            'tasks': [],
            'masumi_integration': {
                'payment_service': self.config.payment_service_url,
                'network': self.config.network,
                'agent_forge_bridge': True
            }
        }
        
        # Export agents
        for name, agent_info in self.agents.items():
            crewai_agent = agent_info['crewai_agent']
            wrapped_agent = agent_info['wrapped_agent']
            
            crewai_config['agents'][name] = {
                'role': crewai_agent.role,
                'goal': crewai_agent.goal,
                'backstory': crewai_agent.backstory,
                'tools': crewai_agent.tools,
                'verbose': crewai_agent.verbose,
                'memory': crewai_agent.memory,
                'masumi_did': wrapped_agent.agent_did,
                'price_ada': wrapped_agent.price_ada,
                'framework': 'Agent Forge'
            }
        
        # Export tasks  
        for i, task in enumerate(self.tasks):
            crewai_config['tasks'].append({
                'id': i + 1,
                'description': task.description,
                'agent': task.agent_type,
                'expected_output': task.expected_output,
                'tools': task.tools,
                'context': task.context
            })
        
        return crewai_config


async def example_web_research_workflow():
    """Example: Multi-agent web research workflow using Agent Forge + CrewAI + Masumi."""
    
    print("🔍 Web Research Workflow Example")
    print("=" * 40)
    
    # Initialize the CrewAI adapter
    adapter = MasumiCrewAIAdapter()
    
    # Add Agent Forge agents to CrewAI workflow
    
    # 1. Web Navigator Agent
    navigator = SimpleNavigationAgent()
    adapter.add_agent_forge_agent(
        name="web_navigator",
        agent_forge_agent=navigator,
        crewai_role="Web Navigator",
        crewai_goal="Navigate to websites and extract basic information",
        crewai_backstory="You are an expert web navigator with the ability to access any website and extract key information efficiently.",
        price_ada=2.0
    )
    
    # 2. Data Compiler Agent  
    compiler = DataCompilerAgent()
    adapter.add_agent_forge_agent(
        name="data_compiler",
        agent_forge_agent=compiler,
        crewai_role="Data Analyst",
        crewai_goal="Compile and analyze data from multiple sources",
        crewai_backstory="You are a skilled data analyst who can process information from various sources and create comprehensive reports.",
        price_ada=8.0
    )
    
    # Add tasks to the workflow
    adapter.add_task(
        description="Navigate to https://httpbin.org/html and extract the page title and main content",
        agent_name="web_navigator",
        expected_output="Page title and content summary",
        context={"url": "https://httpbin.org/html"}
    )
    
    adapter.add_task(
        description="Navigate to https://httpbin.org/json and extract the JSON data structure",
        agent_name="web_navigator", 
        expected_output="JSON data analysis",
        context={"url": "https://httpbin.org/json"}
    )
    
    adapter.add_task(
        description="Compile the extracted data from both sources into a comprehensive report",
        agent_name="data_compiler",
        expected_output="Comprehensive data analysis report",
        context={
            "sources": ["httpbin.org/html", "httpbin.org/json"],
            "report_type": "web_research_summary"
        }
    )
    
    # Execute the workflow
    results = await adapter.execute_workflow("web_research_workflow")
    
    # Export CrewAI configuration
    config = adapter.export_crewai_config()
    
    print(f"\n📋 CrewAI Configuration:")
    print(json.dumps(config, indent=2))
    
    return results


async def example_blockchain_analysis_workflow():
    """Example: Blockchain analysis workflow with multiple Agent Forge agents."""
    
    print("⛓️ Blockchain Analysis Workflow Example")
    print("=" * 40)
    
    adapter = MasumiCrewAIAdapter()
    
    # Add specialized agents for blockchain analysis
    navigator = SimpleNavigationAgent()
    adapter.add_agent_forge_agent(
        name="blockchain_scanner",
        agent_forge_agent=navigator,
        crewai_role="Blockchain Scanner",
        crewai_goal="Scan blockchain explorers and extract transaction data",
        crewai_backstory="You are a blockchain analysis expert who can navigate various blockchain explorers and extract meaningful transaction data.",
        price_ada=5.0
    )
    
    compiler = DataCompilerAgent()
    adapter.add_agent_forge_agent(
        name="crypto_analyst",
        agent_forge_agent=compiler,
        crewai_role="Crypto Market Analyst", 
        crewai_goal="Analyze cryptocurrency market data and generate insights",
        crewai_backstory="You are a seasoned cryptocurrency analyst with deep knowledge of market patterns and blockchain technology.",
        price_ada=12.0
    )
    
    # Add blockchain analysis tasks
    adapter.add_task(
        description="Scan Cardano explorer for recent high-value transactions",
        agent_name="blockchain_scanner",
        expected_output="List of recent high-value transactions with metadata",
        context={
            "blockchain": "cardano",
            "explorer_url": "https://cardanoscan.io",
            "min_value": 10000
        }
    )
    
    adapter.add_task(
        description="Analyze transaction patterns and generate market insights",
        agent_name="crypto_analyst",
        expected_output="Comprehensive blockchain analysis report",
        context={
            "analysis_type": "transaction_pattern_analysis",
            "blockchain": "cardano",
            "timeframe": "24h"
        }
    )
    
    # Execute blockchain workflow
    results = await adapter.execute_workflow("blockchain_analysis_workflow")
    
    return results


if __name__ == "__main__":
    print("🌟 Agent Forge + Masumi + CrewAI Integration Examples")
    print("=" * 60)
    
    async def run_crewai_examples():
        # Run web research workflow
        print("\n🎯 Example 1: Web Research Workflow")
        web_results = await example_web_research_workflow()
        
        print(f"\n📊 Web Research Results:")
        print(f"   Tasks completed: {len(web_results['task_results'])}")
        print(f"   Total cost: {web_results['total_cost_ada']} ADA")
        print(f"   Success: {web_results['success']}")
        
        # Run blockchain analysis workflow
        print(f"\n🎯 Example 2: Blockchain Analysis Workflow")
        blockchain_results = await example_blockchain_analysis_workflow()
        
        print(f"\n📊 Blockchain Analysis Results:")
        print(f"   Tasks completed: {len(blockchain_results['task_results'])}")
        print(f"   Total cost: {blockchain_results['total_cost_ada']} ADA")
        print(f"   Success: {blockchain_results['success']}")
        
        print(f"\n🎉 All CrewAI integration examples completed!")
    
    asyncio.run(run_crewai_examples())
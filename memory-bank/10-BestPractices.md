# ✅ Best Practices: Agent Forge Development

**Purpose:** This document outlines the **agreed-upon standard practices** and **operational guidelines** derived from framework development experiences. It serves as a prescriptive guide for what we have established as the correct way to approach common tasks in Agent Forge framework development.

*Last Updated: June 14, 2025 - Framework Development Best Practices with Enterprise Agent Integration Complete*

**Scope:**
*   ✅ INCLUDED: 
    * Standard operating procedures for framework development, agent creation, CLI usage, and maintenance
    * Established patterns that should be followed in future framework work
    * Practical guidelines for specific framework scenarios we've encountered
    * Recommended approaches for common agent development tasks
*   ❌ EXCLUDED (See Linked Files):
    * **Specific Framework Learnings/Observations:** See framework documentation for factual discoveries and insights
    * **Specific Development Narratives:** See `@12-deadEnd.md` for detailed development stories
    * **Failed Approaches to Avoid:** See `@12-deadEnd.md` for approaches that didn't work
    * **Framework Progress History:** See `@03-progress.md` for timeline of framework development
    * **Technical Details/Context:** See `@07-techContext.md` for foundational technical information

---

# Best Practices for Framework Development & Agent Creation

This document captures key best practices derived from Agent Forge framework development experiences to improve efficiency and reduce recurring issues.

## 1. Framework Memory Bank Usage (Mandated Framework Pattern)

*   **Mandatory Pre-Development Review:** Before starting *any* new agent development or framework task, **thoroughly read ALL relevant files** in the `memory-bank/` directory (@02-activeContext.md, @03-progress.md, @06-systemPatterns.md, @07-techContext.md, @08-PRD.md, etc.) to understand framework patterns and established practices.
    *   **Goal:** Leverage established framework patterns and avoid reinventing solved problems.
    *   **Impact:** Ensures consistent framework usage and leverages collective framework knowledge.

## 2. BaseAgent Inheritance Pattern (Core Framework Practice)

*   **Always Inherit from BaseAgent:** When creating new agents, **always inherit from the BaseAgent class** and follow established patterns:
    1.  Import BaseAgent: `from extraction.agents.base import BaseAgent`
    2.  Implement required abstract methods, especially `async def run()`
    3.  Use `async def _initialize()` for agent-specific setup
    4.  Use `async def _cleanup()` for resource cleanup
    5.  **Verify agent follows patterns** before integration
    *   **Goal:** Ensure consistent agent interface and lifecycle management.
    *   **Impact:** Provides standardized agent behavior and framework compatibility.

**Example Best Practice:**
```python
from extraction.agents.base import BaseAgent

class MyAgent(BaseAgent):
    """Custom agent following framework patterns."""
    
    async def _initialize(self):
        """Agent-specific initialization."""
        self.logger.info("Initializing MyAgent")
        # Setup agent resources here
    
    async def run(self, *args, **kwargs):
        """Main agent logic implementation."""
        if not self.is_ready():
            raise RuntimeError("Agent not ready")
        
        self.logger.info("Running MyAgent")
        # Agent implementation here
        return "Agent completed successfully"
    
    async def _cleanup(self):
        """Agent-specific cleanup."""
        self.logger.info("Cleaning up MyAgent")
        # Cleanup resources here
```

## 3. CLI Interface Usage (Framework Standard)

*   **Use CLI for Agent Management:** Always use the CLI interface for agent operations and follow established command patterns:
    1.  **List agents:** `python cli.py list` to see available agents
    2.  **Run agents:** `python cli.py run agent_name` for execution
    3.  **Debug mode:** `python cli.py --verbose run agent_name` for debugging
    4.  **Version check:** `python cli.py --version` for framework version
    *   **Goal:** Consistent agent management and execution across framework.
    *   **Impact:** Standardized developer experience and framework usage patterns.

## 4. Core Utilities Access (Framework Pattern)

*   **Use Framework Utilities:** Access framework utilities through established import patterns:
    ```python
    # Correct framework utility access
    from agent_forge.core.shared.ai import embeddings
    from agent_forge.core.shared.database import client
    from agent_forge.core.shared.ml import models
    
    class MyAgent(BaseAgent):
        async def run(self):
            # Use framework utilities
            ai_client = embeddings.get_client()
            db_connection = client.get_database()
            ml_model = models.load_model("my_model")
    ```
    *   **Goal:** Leverage framework utilities instead of external dependencies.
    *   **Impact:** Maintains framework self-contained architecture and consistency.

## 5. Async Pattern Usage (Framework Standard)

*   **Follow Async Patterns:** Use async/await patterns consistently throughout agent implementations:
    1.  **All agent methods async:** Use `async def` for agent methods
    2.  **Await framework calls:** Use `await` for framework operations
    3.  **Proper error handling:** Handle async exceptions appropriately
    4.  **Resource management:** Use async context managers when needed
    *   **Goal:** Consistent async patterns throughout framework.
    *   **Impact:** Optimal performance and modern Python development practices.

## 6. Configuration Management (Framework Practice)

*   **Use BaseAgent Configuration:** Leverage BaseAgent configuration system for agent parameters:
    ```python
    class MyAgent(BaseAgent):
        def __init__(self, name=None, config=None):
            super().__init__(name, config)
            
            # Access configuration through BaseAgent
            self.api_key = self.config.get('api_key')
            self.timeout = self.config.get('timeout', 30)
            self.debug_mode = self.config.get('debug', False)
    ```
    *   **Goal:** Consistent configuration management across all agents.
    *   **Impact:** Standardized agent configuration and runtime flexibility.

## 7. Error Handling Standards (Framework Pattern)

*   **Implement Comprehensive Error Handling:** Use framework error handling patterns:
    ```python
    class MyAgent(BaseAgent):
        async def run(self, *args, **kwargs):
            try:
                # Agent logic here
                result = await self.perform_task()
                return result
            except Exception as e:
                self.logger.error(f"Agent execution failed: {e}")
                # Handle error gracefully
                raise
    ```
    *   **Goal:** Consistent error handling and logging across framework.
    *   **Impact:** Better debugging experience and framework reliability.

## 8. Documentation Standards (Framework Practice)

*   **Document Agent Purpose:** Always include clear documentation for agent implementations:
    ```python
    class MyAgent(BaseAgent):
        """
        Custom agent for specific task automation.
        
        This agent performs [specific task] by [brief description].
        
        Usage:
            agent = MyAgent(config={'api_key': 'key'})
            result = await agent.run()
        """
    ```
    *   **Goal:** Clear understanding of agent purpose and usage.
    *   **Impact:** Better framework adoption and developer experience.

## 9. Example-Driven Development (Framework Standard)

*   **Reference Framework Examples:** Always review existing examples before creating new agents:
    1.  **Check examples directory:** Review `examples/` for similar patterns
    2.  **Follow established patterns:** Use examples as reference implementations
    3.  **Validate against examples:** Ensure new agents follow example patterns
    4.  **Add to examples:** Consider adding new agents to examples library
    *   **Goal:** Consistent framework usage and pattern adoption.
    *   **Impact:** Accelerated development and framework consistency.

## 10. Testing and Validation (Framework Practice)

*   **Test Agent Implementation:** Always validate agent functionality:
    ```bash
    # Test agent through CLI
    python cli.py run my_agent
    
    # Test BaseAgent compliance
    python -c "from my_agent import MyAgent; print('Agent import successful')"
    
    # Validate async patterns
    python extraction/agents/base.py  # Test BaseAgent functionality
    ```
    *   **Goal:** Ensure agent functionality and framework compliance.
    *   **Impact:** Reliable agents and framework stability.

## 11. Framework Extension Guidelines (Best Practice)

*   **Extend Framework Properly:** When adding new framework capabilities:
    1.  **Add to core/shared/:** Place new utilities in appropriate core directory
    2.  **Follow import patterns:** Use consistent import patterns
    3.  **Document new utilities:** Provide clear documentation and examples
    4.  **Test integration:** Ensure new utilities work with existing framework
    *   **Goal:** Maintain framework architecture and consistency.
    *   **Impact:** Framework growth without breaking existing functionality.

## 12. Performance Optimization (Framework Standard)

*   **Optimize Agent Performance:** Follow performance best practices:
    1.  **Lazy loading:** Load resources only when needed
    2.  **Resource cleanup:** Properly clean up resources in `_cleanup()`
    3.  **Async optimization:** Use async patterns for I/O operations
    4.  **Memory management:** Avoid memory leaks in long-running agents
    *   **Goal:** Efficient framework operation and resource usage.
    *   **Impact:** Better framework performance and scalability.

## 13. Debugging and Troubleshooting (Framework Practice)

*   **Use Framework Debugging Tools:** Leverage framework debugging capabilities:
    ```bash
    # Enable verbose logging
    python cli.py --verbose run my_agent
    
    # Check agent status
    python -c "from my_agent import MyAgent; agent = MyAgent(); print(agent.get_status())"
    
    # Validate framework utilities
    python -c "import agent_forge.core.shared; print('Framework utilities available')"
    ```
    *   **Goal:** Effective debugging and issue resolution.
    *   **Impact:** Faster problem resolution and development iteration.

## 14. Version Compatibility (Framework Standard)

*   **Maintain Framework Compatibility:** Ensure agent compatibility with framework versions:
    1.  **Use stable APIs:** Rely on documented framework interfaces
    2.  **Test compatibility:** Validate agents with framework updates
    3.  **Handle deprecation:** Update agents when framework APIs change
    4.  **Document requirements:** Specify framework version requirements
    *   **Goal:** Long-term agent functionality and framework evolution.
    *   **Impact:** Stable agent ecosystem and framework adoption.

## 15. Community Contribution (Framework Practice)

*   **Follow Contribution Guidelines:** When contributing to framework:
    1.  **Code quality:** Follow framework coding standards
    2.  **Documentation:** Include comprehensive documentation
    3.  **Testing:** Validate all contributions thoroughly
    4.  **Examples:** Provide usage examples for new features
    *   **Goal:** High-quality framework contributions and community growth.
    *   **Impact:** Framework improvement and community engagement.

---

## Framework Development Workflow Best Practices

### Pre-Development Checklist
- [ ] Read relevant memory-bank documentation
- [ ] Review existing examples for similar patterns
- [ ] Understand BaseAgent interface requirements
- [ ] Plan agent configuration and parameters

### During Development Checklist
- [ ] Inherit from BaseAgent class
- [ ] Implement required abstract methods
- [ ] Use framework utilities instead of external dependencies
- [ ] Follow async patterns throughout implementation
- [ ] Include comprehensive error handling and logging

### Post-Development Checklist
- [ ] Test agent through CLI interface
- [ ] Validate BaseAgent compliance
- [ ] Document agent purpose and usage
- [ ] Consider adding to examples library
- [ ] Verify performance and resource cleanup

### Framework Extension Checklist
- [ ] Add utilities to appropriate core/shared/ directory
- [ ] Follow established import patterns
- [ ] Document new utilities with examples
- [ ] Test integration with existing framework
- [ ] Update framework documentation if needed

---

## Common Anti-Patterns to Avoid

### ❌ Direct External Dependencies
```python
# Avoid: Direct external library usage
import requests
import openai

# Prefer: Framework utility usage
from agent_forge.core.shared.web import requests
from agent_forge.core.shared.ai import openai
```

### ❌ Non-BaseAgent Classes
```python
# Avoid: Custom agent base classes
class MyCustomAgent:
    def run(self):
        pass

# Prefer: BaseAgent inheritance
class MyAgent(BaseAgent):
    async def run(self):
        pass
```

### ❌ Synchronous Patterns
```python
# Avoid: Synchronous implementations
def run(self):
    result = some_operation()
    return result

# Prefer: Async patterns
async def run(self):
    result = await some_operation()
    return result
```

### ❌ Poor Error Handling
```python
# Avoid: Silent failures
async def run(self):
    try:
        result = await operation()
    except:
        pass  # Silent failure

# Prefer: Proper error handling
async def run(self):
    try:
        result = await operation()
    except Exception as e:
        self.logger.error(f"Operation failed: {e}")
        raise
```

---

## Framework Success Metrics

### Code Quality Metrics
- **BaseAgent Usage:** 100% of new agents inherit from BaseAgent
- **Async Patterns:** All agent methods use async/await properly
- **Error Handling:** Comprehensive error handling in all agents
- **Documentation:** All agents include purpose and usage documentation

### Performance Metrics
- **Initialization Time:** Agents initialize in <2 seconds
- **Resource Cleanup:** No resource leaks in agent lifecycle
- **Memory Usage:** Efficient memory usage patterns
- **Framework Overhead:** <5% overhead from framework usage

### Developer Experience Metrics
- **Setup Time:** <30 minutes from framework clone to first agent
- **Pattern Consistency:** Consistent patterns across all agents
- **Debugging Efficiency:** Quick issue identification and resolution
- **Community Adoption:** Growing usage of framework patterns

---

**Framework Philosophy:** Agent Forge prioritizes developer productivity, consistent patterns, and professional quality. These best practices ensure framework success and community adoption.

*Last Updated: June 14, 2025 - Framework development best practices established for Agent Forge*
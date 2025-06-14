---
Title: Agent Forge Framework Maintenance Guide
Purpose: Comprehensive operational procedures for maintaining, monitoring, and troubleshooting the Agent Forge framework
---

# 🛠️ Agent Forge Framework Maintenance Guide

*Last Updated: June 14, 2025 - Framework Architecture Complete - BaseAgent Foundation and CLI Interface Operational*

**Purpose:** This document provides comprehensive guidance for **maintaining, monitoring, and troubleshooting** the Agent Forge framework with its self-contained architecture and comprehensive utilities.

**📋 FRAMEWORK REFERENCES:** For complete technical specifications, see the authoritative framework documentation:
- **[BaseAgent Implementation](../extraction/agents/base.py)** - Core BaseAgent class with async support and standard interface
- **[CLI Implementation](../cli.py)** - Command-line interface with argparse and agent management
- **[Core Utilities](../core/shared/)** - Self-contained dependency system with AI, database, ML utilities
- **[Example Library](../examples/)** - Working agent implementations demonstrating framework patterns
- **[Framework Patterns](06-systemPatterns.md)** - Architecture patterns and design principles
- **[Framework Technologies](07-techContext.md)** - Technology stack and implementation details
- **[Framework Context](05-productContext.md)** - Developer value proposition and use cases

**Scope:**
*   ✅ INCLUDED: Framework overview, CLI maintenance, BaseAgent monitoring, utility management, common issues & troubleshooting, operational procedures, performance optimization.
*   ❌ EXCLUDED (See Linked Files):
    *   **Framework Development Process:** See [01-README-DevProcess.md](01-README-DevProcess.md)
    *   **Framework Requirements:** See [08-PRD.md](08-PRD.md) for comprehensive feature specifications
    *   **Development Best Practices:** See [10-BestPractices.md](10-BestPractices.md)
    *   **Framework Progress:** See [03-progress.md](03-progress.md) for implementation status
    *   **Technology Implementation:** See [07-techContext.md](07-techContext.md)
    *   **Framework Tasks:** See [09-TASKS.md](09-TASKS.md) for development planning

---

# Agent Forge Framework Maintenance & Troubleshooting Guide

## 1. Framework Overview & Monitoring

Agent Forge is a self-contained AI web agent development framework with comprehensive architecture and utilities:

### Core Framework Components (Architecture Complete - June 14, 2025)

1. **BaseAgent Foundation (`extraction/agents/base.py`):** 
   * **Comprehensive base class** with async support and standard interface
   * Provides lifecycle management (initialize, run, cleanup)
   * **Built-in Features:** Configuration management, error handling, status reporting
   * **Performance:** <100ms initialization, async-optimized operations
   * **Validation Status:** Complete implementation with working examples

2. **CLI Interface (`cli.py`):**
   * **Command-line management system** with argparse-based operations
   * Agent discovery, execution, and management capabilities
   * Verbose logging and debugging support with comprehensive help system
   * **Commands:** `list`, `run`, `--version`, `--verbose` with parameter support
   * **Performance:** <50ms command parsing, <200ms agent discovery

3. **Core Utilities (`core/shared/`):**
   * **Self-contained dependency system** with AI, database, ML, and web utilities
   * No external dependencies required for framework operation
   * Modular organization with consistent import patterns
   * **Categories:** AI processing, database operations, ML utilities, authentication, web automation

4. **Example Library (`examples/`):**
   * **20+ working agent implementations** demonstrating framework patterns
   * Progressive complexity from simple to advanced examples
   * All examples inherit from BaseAgent with clear documentation
   * **Usage Patterns:** Data extraction, processing, automation, integration agents

### Framework Health & Monitoring System

5. **Built-in Framework Monitoring:**
   * **BaseAgent Status Reporting**: Health monitoring and lifecycle tracking
   * **CLI Diagnostics**: Command execution monitoring and error reporting
   * **Utility Monitoring**: Core utility performance and error tracking
   * **Example Validation**: Automated testing of example implementations

### Quick Framework Health Checks

```bash
# List all available agents
python cli.py list

# Check framework version
python cli.py --version

# Test BaseAgent foundation
python extraction/agents/base.py

# Validate core utilities
python -c "import agent_forge.core.shared; print('Framework utilities operational')"

# Run example agent with verbose logging
python cli.py --verbose run simple_agent
```

> **For detailed framework usage**: See [01-README-DevProcess.md](01-README-DevProcess.md)

## 2. Framework Status Checks

### Framework Health Assessment

**Primary Method**: Use the CLI interface for comprehensive framework status:

```bash
# Framework health assessment
python cli.py list

# Check specific agent status
python cli.py run agent_name --dry-run

# Framework version and capabilities
python cli.py --version
```

### Core Component Validation

**BaseAgent Foundation Check:**

```bash
# Test BaseAgent implementation
python extraction/agents/base.py

# Expected output: BaseAgent class operational with async support
```

**CLI Interface Validation:**
```bash
# Test CLI command discovery
python cli.py list

# Expected output: List of available agents with descriptions
# Example:
# Available agents:
#   simple_agent          - Basic agent example
#   web_scraper_agent     - Web scraping demonstration
#   data_processor_agent  - Data processing example
```

**Core Utilities Status:**
```bash
# Test core utilities import
python -c "
import agent_forge.core.shared.ai as ai_utils
import agent_forge.core.shared.database as db_utils
import agent_forge.core.shared.ml as ml_utils
print('✅ Core utilities operational')
"

# Expected output: ✅ Core utilities operational
```

**Example Library Validation:**
```bash
# Test example agent execution
python cli.py --verbose run simple_agent

# Expected output: Agent initialization, execution, and cleanup logs
```

**Framework Health Indicators:**
- ✅ **All agents listed**: Framework discovery working properly
- ✅ **BaseAgent imports successfully**: Foundation class operational
- ✅ **Core utilities accessible**: Self-contained dependencies working
- ✅ **Examples run successfully**: Framework integration complete
- ❌ **Import errors**: Missing dependencies or configuration issues
- ⚠️ **Slow initialization (>2s)**: Performance optimization needed

### Framework Performance Assessment

**Use the built-in framework diagnostics for performance evaluation:**

```bash
# Framework timing analysis
time python cli.py list  # Should complete in <200ms

# Agent initialization performance
time python cli.py run simple_agent --profile

# Memory usage monitoring
python -c "
import psutil
import agent_forge.core.shared
print(f'Memory usage: {psutil.Process().memory_info().rss / 1024 / 1024:.1f}MB')
"
```

**Framework Performance Baselines**:
- **CLI Command Parsing**: <50ms for all commands
- **Agent Discovery**: <200ms for agent listing
- **BaseAgent Initialization**: <100ms per agent
- **Core Utility Loading**: <500ms per module (lazy loading)
- **Example Execution**: Varies by complexity, typically <10s for simple examples

### Comprehensive Framework Testing

To run the comprehensive framework validation:

```bash
# Test all framework components
python -c "
from extraction.agents.base import BaseAgent
import agent_forge.core.shared
print('✅ Framework components operational')
"

# Test all examples
for agent in $(python cli.py list | grep -v 'Available agents:' | awk '{print $1}'); do
    echo 'Testing $agent...'
    python cli.py run $agent --validate
done
```

The framework testing will validate BaseAgent inheritance, CLI integration, and core utility access.
See [10-BestPractices.md](10-BestPractices.md) for detailed testing patterns.

### Agent Development Environment Checks

**Primary Method:** Validate development environment setup:

```bash
# Check Python version compatibility
python --version  # Should be 3.8+

# Verify framework imports
python -c "
from extraction.agents.base import BaseAgent
print('✅ BaseAgent foundation available')
"

# Test CLI functionality
python cli.py --help  # Should show comprehensive help
```

## 3. Framework Troubleshooting Guide

> **🔗 Framework Documentation:** All framework references can be found in the [memory-bank/](memory-bank/) documentation

### 3.0. Framework-First Troubleshooting Approach

**Always start with the framework diagnostics for faster issue identification:**

#### Step 1: Framework Health Assessment
```bash
# Get immediate framework status
python cli.py list

# Look for issues in the output:
# - No agents listed (discovery problems)
# - Import errors (dependency issues)
# - Command failures (CLI integration problems)
```

#### Step 2: Check BaseAgent Foundation
```bash
# Test BaseAgent foundation
python extraction/agents/base.py

# Common patterns to verify:
# - BaseAgent class imports successfully
# - Async patterns working correctly
# - Status reporting functional
# - Configuration management operational
```

#### Step 3: Validate Core Utilities
```bash
# Test core utility access
python -c "
try:
    import agent_forge.core.shared.ai
    import agent_forge.core.shared.database
    import agent_forge.core.shared.ml
    print('✅ All core utilities accessible')
except ImportError as e:
    print(f'❌ Utility import failed: {e}')
"

# Check utility organization:
# 1. AI processing utilities available
# 2. Database operation utilities accessible
# 3. ML utility modules importable
# 4. Authentication utilities functional
# 5. Web automation utilities operational
```

#### Step 4: Example Validation
```bash
# Test example agent execution
python cli.py --verbose run simple_agent

# Look for patterns:
# - Successful BaseAgent inheritance
# - Proper async lifecycle execution
# - Clean error handling and logging
# - Resource cleanup completion
```

> **Framework guides**: See [01-README-DevProcess.md](01-README-DevProcess.md) for development workflow

### 3.1. CLI Interface Issues

**Issue: CLI Commands Not Working**
* **Symptom:** `python cli.py` commands fail or show no agents.
* **Troubleshooting:**
  * Verify CLI script is executable and accessible:
    ```bash
    ls -la cli.py
    python cli.py --version
    ```
  * Check for Python import errors:
    ```bash
    python -c "import cli; print('✅ CLI module imports successfully')"
    ```
  * Verify framework directory structure:
    ```bash
    ls -la extraction/agents/
    ls -la core/shared/
    ls -la examples/
    ```
  * Test CLI with verbose logging:
    ```bash
    python cli.py --verbose list
    ```

**Issue: "No agents found" Error**
* **Symptom:** CLI shows no agents available when running `python cli.py list`.
* **Troubleshooting:**
  * Check agent discovery mechanism:
    ```bash
    python -c "
    import os
    print('Examples directory contents:')
    for f in os.listdir('examples'):
        if f.endswith('.py') and not f.startswith('__'):
            print(f'  {f}')
    "
    ```
  * Verify example agents are properly structured:
    ```bash
    python -c "
    from examples.simple_agent import SimpleAgent
    print('✅ Example agent imports successfully')
    "
    ```
  * Check for BaseAgent inheritance in examples:
    ```bash
    grep -r "BaseAgent" examples/
    ```

### 3.2. BaseAgent Issues

**Issue: BaseAgent Import Failures**
* **Symptom:** Unable to import BaseAgent class or agents fail to inherit properly.
* **Troubleshooting:**
  * Check BaseAgent file exists and is accessible:
    ```bash
    ls -la extraction/agents/base.py
    python -c "from extraction.agents.base import BaseAgent; print('✅ BaseAgent imports successfully')"
    ```
  * Verify Python path and module structure:
    ```bash
    python -c "
    import sys
    print('Python path:')
    for p in sys.path:
        print(f'  {p}')
    "
    ```
  * Test BaseAgent functionality directly:
    ```bash
    python extraction/agents/base.py
    ```
  * Check for missing dependencies or import errors:
    ```bash
    python -c "
    import asyncio
    from abc import ABC, abstractmethod
    print('✅ Required dependencies available')
    "
    ```

**Issue: Agent Initialization Failures**
* **Symptom:** Agents fail during initialization or don't respond to run commands.
* **Troubleshooting:**
  * Test agent initialization directly:
    ```bash
    python -c "
    from examples.simple_agent import SimpleAgent
    agent = SimpleAgent()
    print(f'Agent status: {agent.get_status()}')
    "
    ```
  * Check async patterns and lifecycle:
    ```bash
    python -c "
    import asyncio
    from examples.simple_agent import SimpleAgent
    
    async def test_agent():
        agent = SimpleAgent()
        success = await agent.initialize()
        print(f'Initialization: {success}')
        await agent.cleanup()
    
    asyncio.run(test_agent())
    "
    ```
  * Common issues:
    * Missing async/await patterns
    * Incorrect BaseAgent inheritance
    * Configuration parameter problems
    * Resource initialization failures

**Issue: Agent Execution Errors**
* **Symptom:** Agents start but fail during execution with runtime errors.
* **Troubleshooting:**
  * Run agent with verbose logging:
    ```bash
    python cli.py --verbose run agent_name
    ```
  * Common causes include:
    * Unhandled exceptions in agent logic
    * Missing configuration parameters
    * Resource access failures
    * Async pattern violations

### 3.3. Core Utilities Issues

**Issue: Core Utility Import Failures**
* **Symptom:** Framework utilities cannot be imported or accessed.
* **Troubleshooting:**
  * Check core utilities directory structure:
    ```bash
    ls -la core/shared/
    ls -la core/shared/ai/
    ls -la core/shared/database/
    ls -la core/shared/ml/
    ```
  * Test individual utility imports:
    ```bash
    python -c "
    try:
        import agent_forge.core.shared.ai
        print('✅ AI utilities available')
    except ImportError as e:
        print(f'❌ AI utilities failed: {e}')
    "
    ```
  * Verify __init__.py files exist:
    ```bash
    find core/ -name "__init__.py" -exec ls -la {} \;
    ```
  * Check Python path configuration for framework access.

**Issue: Utility Functionality Problems**
* **Symptom:** Utilities import but fail during execution.
* **Troubleshooting:**
  * Test utility functionality directly:
    ```python
    # Test AI utilities
    python -c "
    from agent_forge.core.shared.ai import embeddings
    client = embeddings.get_client()
    print('✅ AI utilities functional')
    "
    ```
  * Check for missing dependencies within utilities:
    ```bash
    python -c "
    import inspect
    from agent_forge.core.shared import ai
    print('AI utility functions:')
    for name, obj in inspect.getmembers(ai):
        if inspect.isfunction(obj):
            print(f'  {name}')
    "
    ```
  * Verify utility configurations and parameters.

**Issue: Self-Contained Dependency Problems**
* **Symptom:** Framework claims to be self-contained but requires external dependencies.
* **Troubleshooting:**
  * Audit external dependency usage:
    ```bash
    grep -r "import " core/shared/ | grep -v "agent_forge" | head -10
    ```
  * Check for missing local implementations:
    ```bash
    python -c "
    import pkgutil
    import agent_forge.core.shared
    
    for importer, modname, ispkg in pkgutil.walk_packages(
        agent_forge.core.shared.__path__, 
        agent_forge.core.shared.__name__ + '.'
    ):
        print(f'Available module: {modname}')
    "
    ```
  * Review framework requirements and ensure all necessary utilities are included locally.

### 3.4. Example Library Issues

**Issue: Example Agents Not Working**
* **Symptom:** Example agents fail to execute or show import errors.
* **Troubleshooting:**
  * Check example directory structure:
    ```bash
    ls -la examples/
    python -c "
    import os
    examples = [f for f in os.listdir('examples') if f.endswith('.py') and not f.startswith('__')]
    print(f'Found {len(examples)} example files: {examples}')
    "
    ```
  * Test individual example imports:
    ```bash
    python -c "
    from examples.simple_agent import SimpleAgent
    print('✅ Simple agent imports successfully')
    "
    ```
  * Verify BaseAgent inheritance in examples:
    ```bash
    python -c "
    from examples.simple_agent import SimpleAgent
    from extraction.agents.base import BaseAgent
    print(f'Inherits BaseAgent: {issubclass(SimpleAgent, BaseAgent)}')
    "
    ```
  * Check example documentation and usage patterns.

**Issue: Example Agent Execution Failures**
* **Symptom:** Examples import but fail during execution.
* **Troubleshooting:**
  * Run examples with CLI verbose mode:
    ```bash
    python cli.py --verbose run simple_agent
    ```
  * Test example lifecycle directly:
    ```bash
    python -c "
    import asyncio
    from examples.simple_agent import SimpleAgent
    
    async def test():
        agent = SimpleAgent()
        await agent.initialize()
        result = await agent.run()
        await agent.cleanup()
        print(f'Example result: {result}')
    
    asyncio.run(test())
    "
    ```
  * Common issues:
    * Missing async patterns in example implementation
    * Incorrect configuration parameters
    * Resource access problems
    * Framework utility integration issues

### 3.5. InteractionType Implementation Issues

**Issue: "'str' object has no attribute 'value'" Error**
* **Symptom:** API returns 500 error or logs show AttributeError about 'str' object not having 'value' attribute
* **Root Cause:** Inconsistent implementation of InteractionType across the codebase (some places treating it as an enum with .value attribute, others as a class with string attributes)
* **Solution:**
  * The consolidated API (`main_consolidated.py`) has fixed this by removing all .value references from InteractionType usage
  * Ensure any custom implementations or tests properly handle InteractionType as a class with string attributes, not as an enum
  * Use proper type checking before accessing attributes from external data
  * Verify the fix by running the comprehensive test suite:
    ```bash
    export USE_TEST_MODE=true
    export BYPASS_CREDIT_CHECK=true
    python test_consolidated_api_suite.py
    ```

### 3.6. Testing and Development Features

**Test Mode and Credit Bypass**

The consolidated API includes special features for testing:

1. **Credit Check Bypass:**
   * Set `BYPASS_CREDIT_CHECK=true` to skip user credit validation
   * Useful for testing without database modifications
   * Works for both `/v2/chat` and `/v2/query` endpoints
   * Should NEVER be enabled in production

2. **Test Mode:**
   * Set `USE_TEST_MODE=true` to enable mock responses
   * Uses a dedicated `process_chat_with_llm_test` function that:
     * Provides content-specific responses based on query patterns
     * Simulates semantic search results
     * Bypasses actual Vertex AI calls
     * Uses `mock_log_user_interaction` to avoid database errors

3. **Combined Testing:**
   * For complete API testing without external dependencies:
     ```bash
     export USE_TEST_MODE=true
     export BYPASS_CREDIT_CHECK=true
     python test_consolidated_api_suite.py
     ```
   * This configuration allows thorough testing without:
     * Requiring real Vertex AI credentials
     * Consuming user credits
     * Needing access to the database

4. **Port Conflict Resolution:**
   * The test suite automatically handles port conflicts
   * Detects when a port is already in use
   * Increments the port number until finding an available one
   * Reports the selected port in console output

These features significantly improve the development and testing experience, especially in environments without access to all external services.

## 4. Framework Monitoring & Logging

### 4.1. Framework Logging

**Built-in Framework Logging:**
```bash
# Enable verbose logging for all CLI operations
python cli.py --verbose list
python cli.py --verbose run agent_name

# BaseAgent logging patterns
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from extraction.agents.base import BaseAgent
agent = BaseAgent()
print('✅ Framework logging configured')
"

# Check agent-specific logs
python -c "
import logging
from examples.simple_agent import SimpleAgent

# Configure logging to see framework activity
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

agent = SimpleAgent()
print('Agent logger:', agent.logger.name)
"
```

**Framework Log Analysis:**
```bash
# Framework startup and initialization logs
python cli.py --verbose list 2>&1 | grep -E "(INFO|ERROR|WARNING)"

# Agent execution logs with timing
time python cli.py --verbose run simple_agent 2>&1 | grep -E "(initialize|run|cleanup)"

# Core utility access logs
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
import agent_forge.core.shared
print('✅ Core utilities loaded')
" 2>&1 | grep -E "(DEBUG|INFO)"
```

### 4.2. Framework Usage Metrics

**Framework Activity Monitoring:**
```bash
# Count available agents
python -c "
import os
agents = [f for f in os.listdir('examples') if f.endswith('.py') and not f.startswith('__')]
print(f'Available agents: {len(agents)}')
for agent in agents:
    print(f'  - {agent}')
"

# Monitor framework performance
python -c "
import time
import psutil
import os

start_time = time.time()
start_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024

# Import framework components
from extraction.agents.base import BaseAgent
import agent_forge.core.shared

end_time = time.time()
end_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024

print(f'Framework load time: {end_time - start_time:.3f}s')
print(f'Memory usage: {end_memory:.1f}MB (delta: +{end_memory - start_memory:.1f}MB)')
"

# Agent execution statistics
python -c "
import asyncio
import time
from examples.simple_agent import SimpleAgent

async def measure_agent():
    agent = SimpleAgent()
    
    start = time.time()
    await agent.initialize()
    init_time = time.time() - start
    
    start = time.time()
    result = await agent.run()
    run_time = time.time() - start
    
    start = time.time()
    await agent.cleanup()
    cleanup_time = time.time() - start
    
    print(f'Agent timing: init={init_time:.3f}s, run={run_time:.3f}s, cleanup={cleanup_time:.3f}s')
    return result

asyncio.run(measure_agent())
"
```

## 5. Deployment and UX Coordination

*For detailed deployment procedures, refer to [deployment/comprehensive_deployment_guide.md](deployment/comprehensive_deployment_guide.md). This section provides a high-level overview.*

### 5.1. Backend API

**🚀 RECOMMENDED: Automated Deployment**
Use the automated pipeline for reliable deployments with integrated testing:
```bash
# One-command automated deployment with bot update and testing
gcloud builds submit --config=deployment/configs/production/api-automated-deployment.yaml .
```
**What it does:**
- ✅ Deploys API to Cloud Run
- ✅ Automatically updates and restarts Telegram bot on VM
- ✅ Runs comprehensive testing (6 categories)
- ✅ Verifies functionality and generates report
- ✅ Automatic rollback on failure

See [guides/automated_deployment_guide.md](guides/automated_deployment_guide.md) for complete documentation.

**Manual API Deployment (Legacy):**
```bash
# From project root
gcloud builds submit --config deployment/configs/production/api-current.yaml .
```

**Deploy to a Different Service Name:**
```bash
# Modify the service name in the configuration file or use a different config
gcloud builds submit --config deployment/configs/experimental/debug-info-high-memory.yaml .
```

**Roll Back to a Previous Revision:**
```bash
# List revisions
gcloud run revisions list --service=chatbot-api-service-v2 --region=us-central1

# Direct 100% of traffic to a specific revision
gcloud run services update-traffic chatbot-api-service-v2 \
  --to-revisions=chatbot-api-service-v2-00006-xyz=100 \
  --region=us-central1
```

### 5.2. Telegram Bot and UX Coordination

**⚠️ CRITICAL: UX Deployment Coordination**

When deploying UX improvements (event limiting, follow-up questions, etc.), both API and Telegram bot must be updated together to maintain consistency.

**Deploy Updated Bot with UX Coordination:**
```bash
# Copy updated bot.py with UX-compatible text processing
gcloud compute scp chatbot_telegram/bot.py nuru-ai-telegram-bot-vm:~/chatbot_telegram/bot.py --zone=europe-west1-b

# SSH to VM and restart bot service
gcloud compute ssh eladm@nuru-ai-telegram-bot-vm --zone europe-west1-b --command="
  cd chatbot_telegram
  pkill -f 'python bot.py'
  rm -f /tmp/token_navigator_bot.lock
  nohup bash -c 'source venv_bot/bin/activate && python bot.py' > logs/bot_restart.log 2>&1 &
  sleep 3
  ps aux | grep 'python.*bot.py' | head -3
"
```

**UX Testing After Deployment:**
```bash
# Test same query on both platforms
curl -X POST "${API_BASE_URL}/v2/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "tell me about events on april 29 2025", "user_id": "test", "chat_id": "test"}' \
  | jq -r '.message' | head -15

# Should show: "Found 104 events (showing first 3)" and follow-up questions
# Then test identical query on Telegram bot - should show same limited format
```

### 5.6. Deploying a New API Version

If you need to deploy a completely new version of the API service, you can use the following command:

```bash
# Deploy a new version of the API
gcloud builds submit --config deployment/configs/production/api-current.yaml .
```

### 5.7. Fixing Vertex AI Compatibility Issues

To fix issues with Vertex AI compatibility, a wrapper has been created in `chatbot_api/vertex_tools.py`. To deploy a version with enhanced compatibility, use:

```bash
# Deploy with Vertex AI compatibility enhancements
gcloud builds submit --config deployment/configs/production/api-vertex.yaml .
```

### 5.8. Fixing InteractionType Issues

To fix issues with InteractionType usage, a separate deployment configuration has been created. To deploy:

```bash
# Deploy with InteractionType fixes
gcloud builds submit --config deployment/configs/production/api-interactiontype.yaml .
```

### 5.9. Deploying Test Versions

For testing new features or fixes before production deployment:

```bash
# Deploy a test version of the API
gcloud builds submit --config deployment/configs/test/standard-api-test.yaml .

# Deploy a minimal test version for debugging
gcloud builds submit --config deployment/configs/test/minimal-api-test.yaml .
```

### 5.10. Deploying Experimental Features

For experimental features or phased implementations:

```bash
# Deploy a specific phase of the simplified API
gcloud builds submit --config deployment/configs/experimental/simple-api-phase5.yaml .
```

## 6. Framework Routine Maintenance

### 6.1. Recommended Regular Framework Checks

**Daily Development:**
* Verify CLI interface responds correctly: `python cli.py --version`
* Test BaseAgent foundation: `python extraction/agents/base.py`
* Check example agents are discoverable: `python cli.py list`

**Weekly Framework Health:**
* Run comprehensive framework validation:
  ```bash
  # Test all framework components
  python -c "
  from extraction.agents.base import BaseAgent
  import agent_forge.core.shared
  print('✅ Framework components operational')
  "
  
  # Validate examples work
  python cli.py --verbose run simple_agent
  ```
* Review framework performance metrics
* Check for any import or dependency issues

**Monthly Framework Maintenance:**
* Review and update framework documentation
* Check for Python version compatibility
* Update example library with new patterns
* Review core utilities for optimization opportunities

### 6.2. Framework Backup & Version Control

**Framework Code:**
* All framework code is version-controlled in the Git repository
* Key components to protect:
  - `extraction/agents/base.py` (BaseAgent foundation)
  - `cli.py` (CLI interface)
  - `core/shared/` (utility system)
  - `examples/` (example library)
  - `memory-bank/` (documentation)

**Configuration & Customizations:**
* Backup any custom agent implementations
* Version control agent-specific configurations
* Document custom utility additions
* Preserve framework extension patterns

### 6.3. Framework Performance Optimization

**Regular Performance Checks:**
```bash
# Framework startup performance
time python cli.py list

# Memory usage monitoring
python -c "
import psutil
import agent_forge.core.shared
print(f'Memory: {psutil.Process().memory_info().rss / 1024 / 1024:.1f}MB')
"

# Agent execution timing
time python cli.py run simple_agent
```

**Optimization Opportunities:**
* Lazy loading of core utilities
* Agent initialization optimization
* CLI command response time improvement
* Example agent performance tuning

## 7. Framework Documentation References

**Framework Core Documentation:**
* [BaseAgent Implementation](../extraction/agents/base.py): **ESSENTIAL** - Core BaseAgent class reference
* [CLI Implementation](../cli.py): Command-line interface source and usage patterns
* [Core Utilities](../core/shared/): Self-contained utility system documentation
* [Example Library](../examples/): Working agent implementations and patterns

**Framework Development Documentation:**
* [01-README-DevProcess.md](01-README-DevProcess.md): Framework development workflow and process
* [02-activeContext.md](02-activeContext.md): Current framework development focus
* [03-progress.md](03-progress.md): Framework implementation status and milestones
* [04-projectbrief.md](04-projectbrief.md): Framework vision and strategic direction
* [05-productContext.md](05-productContext.md): Developer value proposition and use cases
* [06-systemPatterns.md](06-systemPatterns.md): Framework architecture patterns and principles
* [07-techContext.md](07-techContext.md): Framework technology stack and implementation
* [08-PRD.md](08-PRD.md): Framework requirements and specifications
* [09-TASKS.md](09-TASKS.md): Framework development task management
* [10-BestPractices.md](10-BestPractices.md): Framework development best practices

**External Documentation:**
* [Python AsyncIO Documentation](https://docs.python.org/3/library/asyncio.html): Async patterns used throughout framework
* [Python ABC Documentation](https://docs.python.org/3/library/abc.html): Abstract base class patterns for BaseAgent
* [Python Argparse Documentation](https://docs.python.org/3/library/argparse.html): CLI interface implementation
* [Python Logging Documentation](https://docs.python.org/3/library/logging.html): Framework logging patterns

## 8. Framework Support & Community

*Agent Forge is an open-source framework for the developer community.*

**Framework Maintainer:**
* Name: Elad Mintzer
* Email: eladm@example.com
* GitHub: eladmint

**Community Support:**
* GitHub Issues: For bug reports and feature requests
* Documentation: Complete framework guides in memory-bank/
* Examples: Working implementations in examples/ directory

**Contributing:**
* Follow framework development best practices (see [10-BestPractices.md](10-BestPractices.md))
* All agents should inherit from BaseAgent
* Use framework patterns and conventions
* Add comprehensive documentation for new features

## Troubleshooting Variable Scope Issues in Try/Finally Blocks

### Issue Description

If you encounter an error like this in production logs:
```
"error_details": "Internal server error: cannot unpack non-iterable coroutine object; cannot access free variable 'db_user_uuid_str' where it is not associated with a value in enclosing scope"
```

This indicates a combination of issues:
1. **Variable Scope Issue**: Variables defined inside a try block are being accessed in a finally block
2. **Coroutine Handling Issue**: An async function is not being properly awaited, resulting in a coroutine object

### Root Causes

1. **Python Scope Rules**: Variables defined inside a try block are not guaranteed to be accessible in the finally block, especially if the try block fails before the variable is defined.
2. **Lambda Capturing**: When using lambda functions in a finally block that reference variables from the try block, you can encounter scope issues.
3. **Async Function Handling**: When an async function is called without `await`, it returns a coroutine object that must be awaited before its result can be used.
4. **run_sync with Async Functions**: When passing a lambda that calls an async function to `anyio.to_thread.run_sync()`, the lambda returns a coroutine object, not the function's result.

### Common Patterns That Lead to Problems

#### 1. Variables defined in try used in finally
```python
try:
    # Variable defined here
    db_user_uuid_str = get_uuid()
    # ...more code...
finally:
    # Used here
    log_interaction(db_user_uuid_str)
```

#### 2. Using async functions in synchronous lambdas
```python
# PROBLEMATIC: This passes an async function through a synchronous lambda
user_check_result = await anyio.to_thread.run_sync(
    lambda: utils.check_and_create_user_if_not_exists(  # async function
        user_id=query_request.user_id,
        current_db_client=db,
        logger_instance=logger,
    )
)
# This will fail because user_check_result is a coroutine, not a tuple
db_user_uuid_str, remaining_credits, error_message = user_check_result
```

### Solutions

#### 1. Initialize variables before the try block
```python
# Initialize at function level before try block
db_user_uuid_str = None
remaining_credits = 0
error_message = None

try:
    # Assign values inside try block
    db_user_uuid_str, remaining_credits, error_message = process_user()
    # ...more code...
finally:
    # Now db_user_uuid_str is always defined, even if try block fails
    log_interaction(db_user_uuid_str)
```

#### 2. Use default values in finally block
```python
try:
    # ...code...
finally:
    # Use None/default if variables aren't set
    log_interaction(db_user_uuid_str if 'db_user_uuid_str' in locals() else None)
```

#### 3. Call async functions properly
```python
# CORRECT: If the function is async and you're in an async context, await it directly
db_user_uuid_str, remaining_credits, error_message = await utils.check_and_create_user_if_not_exists(
    user_id=query_request.user_id,
    current_db_client=db,
    logger_instance=logger,
)
```

#### 4. When using run_sync, ensure the function is truly synchronous
```python
# CORRECT: If you need to call a sync function from an async context
result = await anyio.to_thread.run_sync(
    some_cpu_bound_sync_function,
    arg1, arg2
)

# CORRECT: If you need to call an async function but wrap it properly
# Option 1: Use a sync wrapper that awaits the async function
async def async_func():
    return 42

def sync_wrapper():
    import asyncio
    return asyncio.run(async_func())

result = await anyio.to_thread.run_sync(sync_wrapper)

# Option 2: Call async function directly if already in async context
result = await async_func()
```

### Testing for These Issues

1. **Local Testing**: Use `pytest` with explicit tests for error conditions (e.g., exceptions in try blocks)
2. **Code Review**: Look for variables defined in try blocks and used in finally blocks
3. **Static Analysis**: Configure linter rules to warn about specific patterns
4. **Explicit Type Annotations**: Use proper annotations (e.g., `async def`, return types) to make async behavior clear

### Prevention

1. **Initialize Variables Early**: Always initialize variables at the function level before try blocks if they'll be used in finally blocks
2. **Clear Async/Sync Boundaries**: Be explicit about which functions are async and which are sync
3. **Consistent Patterns**: Use consistent patterns for error handling and async/sync transitions
4. **Documentation**: Document complex error handling or async patterns in function docstrings and comments

### Related Issues

For issues with environment variables and comments, see the troubleshooting section in [@environment_variables.md](mdc:memory-bank/environment_variables.md).

### API Runtime Errors: Coroutines and Variable Scope

If you encounter errors like `cannot unpack non-iterable coroutine object` or variable scope issues in try/finally blocks:

- **Root Cause:** This typically happens when an async function is called without using `await`, especially in lambdas passed to `anyio.to_thread.run_sync`. The function returns a coroutine object that must be awaited.

- **Solution:**
  - Make sure async functions are always called with `await` unless you explicitly want to work with the coroutine object
  - Initialize all variables accessed in finally blocks at the function level, not inside try blocks
  - When using `anyio.to_thread.run_sync`, ensure the lambda doesn't call async functions directly without awaiting them
  - For examples of proper patterns, see `chatbot_api/main.py` (fixed in hotfix3, Build ID: 2930d483-6d10-4031-b358-267e77762612)

### Cloud Run Environment Variable Type Conflicts

If you encounter the error `Cannot update environment variable to string literal because it has already been set with a different type`:

- **Root Cause:** Cloud Run environment variables must maintain consistent types. A variable set as a secret reference cannot later be set as a plain environment variable without first clearing it.

- **Solution:**
  - Use `--update-secrets` for modifying existing secret references instead of `--set-secrets`
  - For new deployments, make a conscious choice about whether a variable should be a plain environment variable or a secret reference
  - If needed, use `--clear-secrets=VAR_NAME` followed by `--set-env-vars=VAR_NAME=value` to change type

## Environment Configuration Reference

### Critical Environment Variables

The following environment variables control key behaviors in the system:

| Variable | Purpose | Notes |
|----------|---------|-------|
| `USE_TEST_MODE` | Bypasses authentication requirements | Set to `true` in staging, `false` in production |
| `BYPASS_CREDIT_CHECK` | Skips user credit verification | Set to `true` in staging, `false` in production |
| `DEBUG` | Enables verbose logging | Set to `false` in production |
| `LOG_LEVEL` | Sets logging verbosity | Use `info` or `warning` in production |

#### Testing Mode Configuration

* **USE_TEST_MODE=true**: 
  - Disables JWT validation for authentication
  - Allows any user_id to be passed
  - Simplifies testing of API endpoints
  - **NEVER** enable in production environment

* **BYPASS_CREDIT_CHECK=true**:
  - Skips verification of user's remaining API credits
  - Useful for staging testing without creating real transactions
  - **NEVER** enable in production environment

## Telegram Bot Maintenance and UX Coordination

### UX Deployment Best Practices

**⚠️ CRITICAL**: Always coordinate UX deployments between API and Telegram bot to prevent user experience inconsistencies.

**Common UX Issues:**
- API shows 3 events, Telegram shows 104 events
- Missing follow-up questions in Telegram
- Broken emoji formatting across platforms

**Prevention Checklist:**
1. **Test API UX directly** before bot deployment
2. **Update bot text processing** to preserve UX elements
3. **Test cross-platform consistency** with identical queries
4. **Verify event limiting** works on both interfaces

**For detailed UX testing procedures**: See [guides/ux_testing_guide.md](guides/ux_testing_guide.md)

### Telegram Bot Token Reset Procedure

If the Telegram bot encounters persistent "Conflict: terminated by other getUpdates request" errors despite service restarts and process cleanup, a token reset may be necessary. Follow this procedure:

1. **Identify the issue:**
   - Look for repeated "Conflict: terminated by other getUpdates request" errors in the bot.err log
   - Verify that no other instances of the bot are running with `ps aux | grep bot.py`
   - Confirm that standard remediation steps (service restart, complete process cleanup) have failed

2. **Request a new token from BotFather:**
   - Open Telegram and find BotFather (@BotFather)
   - Send the `/revoke` command
   - Select the Nuru AI bot
   - Confirm the revocation
   - Copy the new token provided by BotFather

3. **Update the token in Google Secret Manager:**
   ```bash
   echo -n "NEW_TOKEN" | gcloud secrets versions add TELEGRAM_BOT_TOKEN --data-file=-
   ```

4. **Deploy with the new token:**
   - Use the `deploy_fixed_bot.sh` script which:
     - Fetches the latest token from Secret Manager
     - Copies the fixed bot.py to the VM
     - Configures the service
     - Restarts the service
   ```bash
   ./deploy_fixed_bot.sh
   ```

5. **Verify the deployment:**
   - Check the service status: `gcloud compute ssh nuru-ai-telegram-bot-vm --zone=europe-west1-b -- "sudo systemctl status token-nav-telegram.service"`
   - Check the logs for successful connections: `gcloud compute ssh nuru-ai-telegram-bot-vm --zone=europe-west1-b -- "tail -50 ~/chatbot_telegram/bot.err"`
   - Verify the bot responds to messages in Telegram

### Important Bot Deployment Notes

- Always use `drop_pending_updates=True` in the `Application.run_polling()` method to prevent the bot from processing old updates that could trigger conflicts
- Ensure proper file locking mechanisms are implemented to prevent multiple bot instances
- The `read_timeout` parameter is not supported in some versions of the Telegram library and should be removed
- After deploying a new bot token, monitor logs for 24-48 hours to ensure stability

For detailed guidance, refer to:
- `telegram_bot_token_reset_guide.md` - Step-by-step guide for token reset
- `telegram_bot_deployment_report.md` - Comprehensive report on deployment issues and solutions
- `memory-bank/adrs/ADR-022-Telegram-Bot-Deployment-Challenges.md` - Architectural decision record

## MCP Browser Control Maintenance

### MCP System Status Check

Check the MCP browser control integration status:

```bash
# Test MCP server functionality
cd mcp_tools
python test_mcp_client.py

# Expected output: Available tools: ['launch_browser', 'navigate_to_url', ...]
```

### MCP Component Health

1. **MCP Server Status:**
   ```bash
   # Check if MCP server builds correctly
   cd mcp_tools
   npm run build
   
   # Verify compiled output
   ls dist/index.js
   ```

2. **Enhanced Scraper Agent:**
   ```bash
   # Test enhanced scraper agent
   python test_mcp_simple.py
   
   # Expected: 100% success rate with timing metrics
   ```

3. **Baseline Metrics Validation:**
   ```bash
   # Check recent MCP performance
   cat mcp_baseline_metrics.json
   
   # Verify success_rate: 1.0 and reasonable response times
   ```

### Common MCP Issues and Solutions

#### Issue: "MCP Server Not Found"
```bash
# Solution: Rebuild MCP server
cd mcp_tools
npm install
npm run build
```

#### Issue: "Browser Launch Failed"
```bash
# Solution: Install browser dependencies
npx playwright install chromium
npx playwright install-deps  # Linux only
```

#### Issue: "Navigation Timeout"
```python
# Solution: Increase timeout in MCP calls
await client.call_tool("navigate_to_url", {
    "url": url,
    "timeout": 60000  # Increase from 30s to 60s
})
```

#### Issue: "Content Extraction Empty"
```python
# Solution: Try different wait conditions
await client.call_tool("navigate_to_url", {
    "waitFor": "load"  # Try "load" instead of "networkidle"
})
```

### MCP Performance Monitoring

Monitor MCP usage and performance:

```python
# Get MCP statistics from enhanced scraper
from agents.mcp_enhanced_scraper_agent import MCPEnhancedScraperAgent

scraper = MCPEnhancedScraperAgent()
stats = scraper.get_statistics()

print(f"MCP fallback usage: {stats['mcp_fallback_rate']:.1%}")
print(f"MCP success rate: {stats['mcp_fallback_success_rate']:.1%}")
print(f"Overall improvement: {stats['overall_success_rate']:.1%}")
```

### MCP Development Debugging

Enable MCP debugging for development:

```python
# Enable debug mode
await client.call_tool("launch_browser", {
    "headless": False,  # Show browser window
    "debug": True       # Slower operation for debugging
})

# Take debugging screenshots
await client.call_tool("take_screenshot", {
    "fullPage": True,
    "path": "debug_screenshot.png"
})
```

### MCP Maintenance Schedule

**Daily:**
- Monitor MCP success rates via statistics
- Check for any MCP-related error logs

**Weekly:**
- Run baseline metrics collection test
- Verify MCP server build and functionality
- Review debugging screenshots if any issues

**Monthly:**
- Evaluate MCP performance trends
- Consider Phase 2 commercial integration based on usage patterns
- Update MCP dependencies if needed

For detailed MCP setup and usage instructions, see:
- `mcp_tools/README.md` - Complete MCP documentation
- `guides/mcp_browser_control_setup.md` - Step-by-step setup guide
- `memory-bank/adrs/ADR-042-MCP-Browser-Control-Integration.md` - Architectural decision record
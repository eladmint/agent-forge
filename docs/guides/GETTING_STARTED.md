# 🚀 Getting Started with Agent Forge

Welcome to Agent Forge! This guide will get you up and running with your first autonomous AI web agent in under 30 minutes.

## 📋 **Prerequisites**

- **Python 3.8+** installed on your system
- **Git** for cloning the repository
- **Basic Python knowledge** (understanding of classes and async/await)

## ⚡ **Quick Start (5 minutes)**

### **1. Clone and Navigate**
```bash
git clone <agent_forge_repository>
cd agent_forge
```

### **2. Test the Framework**
```bash
# List available agents
python cli.py list

# Run the example navigation agent
python cli.py run simple_navigation --url https://example.com
```

### **3. Success!**
If you see the agent running and attempting navigation, you're ready to build agents! 🎉

## 🔧 **Framework Architecture Overview**

Agent Forge uses a simple pattern:

```python
from core.agents.base import BaseAgent

class MyAgent(BaseAgent):
    async def run(self):
        # Your agent logic here
        return "Agent completed successfully!"
```

## 🛠️ **Your First Agent (10 minutes)**

Let's create a simple agent that analyzes web pages:

### **Step 1: Create Your Agent File**
Create `examples/my_first_agent.py`:

```python
"""
My First Agent - A simple web page analyzer
"""

from typing import Optional
from core.agents.base import BaseAgent

class MyFirstAgent(BaseAgent):
    """
    A simple agent that navigates to a URL and extracts basic information.
    """
    
    def __init__(self, name: Optional[str] = None, config: Optional[dict] = None, url: Optional[str] = None):
        super().__init__(name, config)
        self.url: str = url or self.config.get('url', 'https://example.com')
        
    async def run(self) -> Optional[str]:
        """
        Navigate to URL and extract information.
        """
        self.logger.info(f"Analyzing website: {self.url}")
        
        if not self.browser_client:
            self.logger.error("Browser client not available")
            return None
            
        try:
            # Navigate to the URL
            response = await self.browser_client.navigate(self.url)
            
            if response and response.get('page_title'):
                title = response.get('page_title')
                self.logger.info(f"Found page title: {title}")
                print(f"📄 Analyzed page: {title}")
                return f"Analysis complete: {title}"
            else:
                self.logger.warning("Could not extract page information")
                return "Analysis incomplete"
                
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            return None
```

### **Step 2: Test Your Agent**
```bash
# Your agent should now appear in the list
python cli.py list

# Run your agent
python cli.py run my_first --url https://github.com
```

### **Step 3: Understand the Output**
Your agent will:
1. Initialize with the Steel Browser client
2. Navigate to the specified URL
3. Extract and display the page title
4. Log all activities with timestamps

## 🎯 **Key Framework Concepts**

### **BaseAgent Lifecycle**
Every agent follows this pattern:
1. **`__init__`** - Set up agent parameters
2. **`initialize()`** - Set up resources (browser, APIs, etc.)
3. **`run()`** - Execute your agent logic
4. **`cleanup()`** - Clean up resources

### **Browser Integration**
The framework provides `self.browser_client` automatically:
```python
# Navigate to any URL
response = await self.browser_client.navigate(url)

# The response contains page information
title = response.get('page_title')
```

### **Configuration**
Pass configuration through the CLI or constructor:
```bash
# Via CLI arguments
python cli.py run my_agent --url https://example.com

# Via config file (advanced)
python cli.py run my_agent --config my_config.json
```

## 📖 **Next Steps**

### **Learn More**
- **[Agent Development Tutorial](../tutorials/AGENT_DEVELOPMENT_TUTORIAL.md)** - Build more complex agents
- **[BaseAgent API Reference](../api/BASEAGENT_API_REFERENCE.md)** - Complete API documentation
- **[Example Agents](../EXAMPLE_AGENTS.md)** - Study working examples

### **Advanced Features**
- **[NMKR Integration](../integrations/NMKR_PROOF_OF_EXECUTION_GUIDE.md)** - Create blockchain-verified agents
- **[Steel Browser Guide](../integrations/STEEL_BROWSER_INTEGRATION.md)** - Advanced web automation
- **[Best Practices](../BEST_PRACTICES.md)** - Professional development patterns

### **Build Something Awesome**
Ideas for your next agent:
- **Content Monitor** - Track changes on websites
- **Data Collector** - Gather information from multiple sources
- **Report Generator** - Compile and analyze web data
- **Blockchain Auditor** - Create verifiable execution proofs

## ❓ **Having Issues?**

Check the **[Troubleshooting Guide](../TROUBLESHOOTING.md)** for common solutions.

---

**🎉 Congratulations!** You've built your first Agent Forge agent. The framework handles all the complex infrastructure so you can focus on your agent's unique logic.

**Next:** Try the **[Agent Development Tutorial](../tutorials/AGENT_DEVELOPMENT_TUTORIAL.md)** to build more sophisticated agents.
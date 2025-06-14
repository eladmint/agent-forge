# 🖥️ CLI Reference Guide

The Agent Forge command-line interface (CLI) provides a simple and powerful way to manage and execute agents. This guide covers all available commands and options.

## 📋 **Basic Usage**

```bash
python cli.py [COMMAND] [OPTIONS]
```

## 🔧 **Global Options**

| Option | Short | Description |
|--------|-------|-------------|
| `--version` | | Show framework version |
| `--verbose` | `-v` | Enable verbose logging |
| `--help` | `-h` | Show help message |

### **Examples:**
```bash
# Show version
python cli.py --version

# Enable verbose logging for any command
python cli.py --verbose list
python cli.py -v run simple_navigation --url https://example.com
```

## 📝 **Commands**

### **`list` - List Available Agents**

Discovers and displays all available agents in the examples directory.

**Usage:**
```bash
python cli.py list
```

**Output:**
```
Available agents:
  simple_navigation    - A simple agent that navigates to a URL and extracts the page title
  nmkr_auditor        - NMKR Proof-of-Execution demonstration agent
  data_compiler       - Data compilation and processing agent
```

**Details:**
- Automatically scans the `examples/` directory for agent classes
- Shows agent name and description (from class docstring)
- Agents must inherit from `BaseAgent` to be discovered

### **`run` - Execute an Agent**

Runs a specific agent with optional parameters.

**Usage:**
```bash
python cli.py run <agent_name> [OPTIONS]
```

**Agent-Specific Options:**

| Option | Description | Example |
|--------|-------------|---------|
| `--url` | Target URL for navigation agents | `--url https://github.com` |
| `--config` | Path to configuration file | `--config my_config.json` |
| `--dry-run` | Show what would be done without executing | `--dry-run` |

### **Examples:**

**Simple Navigation:**
```bash
# Basic navigation
python cli.py run simple_navigation --url https://example.com

# With verbose logging
python cli.py --verbose run simple_navigation --url https://github.com

# Dry run (show what would happen)
python cli.py run simple_navigation --url https://example.com --dry-run
```

**NMKR Auditor Agent:**
```bash
# Basic audit
python cli.py run nmkr_auditor --url https://example.com

# With task description
python cli.py run nmkr_auditor --url https://cardano.org --task "Analyze Cardano homepage"
```

**Using Configuration Files:**
```bash
# Run with config file
python cli.py run my_agent --config agents/my_config.json
```

**Example Configuration File (`my_config.json`):**
```json
{
  "url": "https://example.com",
  "timeout": 30,
  "debug": true,
  "custom_setting": "value"
}
```

## 🔍 **Agent Discovery**

The CLI automatically discovers agents using these rules:

1. **Location:** Scans the `examples/` directory
2. **Pattern:** Looks for Python files containing classes that inherit from `BaseAgent`
3. **Naming:** Converts `CamelCase` class names to `snake_case` CLI names
   - `SimpleNavigationAgent` → `simple_navigation`
   - `NMKRAuditorAgent` → `nmkr_auditor`
4. **Exclusions:** Ignores files starting with `__` (like `__init__.py`)

## ⚙️ **Advanced Usage**

### **Environment Variables**

Set these environment variables to customize framework behavior:

```bash
# Set log level
export AGENT_FORGE_LOG_LEVEL=DEBUG

# Set configuration directory
export AGENT_FORGE_CONFIG_DIR=./config

# Run agent with environment
python cli.py run my_agent --url https://example.com
```

### **Debugging Agents**

**Enable Verbose Logging:**
```bash
python cli.py --verbose run agent_name --url https://example.com
```

**Check Agent Status:**
```bash
# List agents to verify discovery
python cli.py list

# Test with dry run
python cli.py run agent_name --dry-run
```

**Debug Output Example:**
```
2025-06-14 08:00:00 - agent_forge - INFO - Initializing agent: simple_navigation
2025-06-14 08:00:00 - agent_forge.SimpleNavigationAgent - INFO - Initializing functional browser client...
2025-06-14 08:00:00 - agent_forge.SimpleNavigationAgent - INFO - Functional browser client initialized successfully
2025-06-14 08:00:00 - agent_forge - INFO - Running agent: simple_navigation
2025-06-14 08:00:00 - agent_forge.SimpleNavigationAgent - INFO - Navigating to https://example.com using functional Steel Browser...
```

### **Error Handling**

The CLI provides helpful error messages:

**Agent Not Found:**
```bash
$ python cli.py run nonexistent_agent
Error: Agent 'nonexistent_agent' not found. Use 'list' to see available agents.
```

**Missing Required Parameters:**
```bash
$ python cli.py run simple_navigation
Error: URL must be provided either as parameter or in config
```

**Agent Initialization Failure:**
```bash
$ python cli.py run broken_agent
Error: Failed to initialize agent 'broken_agent': [specific error message]
```

## 🚀 **Performance Tips**

### **Faster Agent Discovery**
- Keep the `examples/` directory clean
- Remove unused agent files
- Use descriptive class names and docstrings

### **Efficient Logging**
```bash
# Normal operation (minimal logging)
python cli.py run agent_name

# Debug mode (detailed logging)
python cli.py --verbose run agent_name

# Silent operation (redirect output)
python cli.py run agent_name > output.log 2>&1
```

## 📖 **Integration with Development**

### **Testing New Agents**
```bash
# 1. Create your agent in examples/
# 2. Test discovery
python cli.py list

# 3. Test execution
python cli.py --verbose run your_agent --dry-run

# 4. Full test
python cli.py run your_agent --url https://example.com
```

### **IDE Integration**
Configure your IDE to run CLI commands:

**VS Code Launch Configuration:**
```json
{
  "name": "Run Agent",
  "type": "python",
  "request": "launch",
  "program": "cli.py",
  "args": ["run", "simple_navigation", "--url", "https://example.com"],
  "console": "integratedTerminal"
}
```

## ❓ **Troubleshooting**

### **Common Issues**

**"No agents found"**
- Check that your agent class inherits from `BaseAgent`
- Ensure the file is in the `examples/` directory
- Verify the Python file doesn't have syntax errors

**"Module import errors"**
- Ensure you're running from the agent_forge root directory
- Check that all required dependencies are available

**"Agent execution failed"**
- Use `--verbose` flag to see detailed error messages
- Check agent logs for specific error information
- Try `--dry-run` to test without execution

For more troubleshooting help, see the **[Troubleshooting Guide](TROUBLESHOOTING.md)**.

---

**Next Steps:**
- **[Getting Started Guide](GETTING_STARTED.md)** - Create your first agent
- **[Agent Development Tutorial](AGENT_DEVELOPMENT_TUTORIAL.md)** - Build complex agents
- **[BaseAgent API Reference](BASEAGENT_API_REFERENCE.md)** - Complete API documentation
"""
Agent Forge Testing Framework

Comprehensive test suite for validating Agent Forge framework components,
agents, and integrations.
"""

import sys
from pathlib import Path

# Add the parent directory to Python path for imports
test_dir = Path(__file__).parent
project_root = test_dir.parent
sys.path.insert(0, str(project_root))
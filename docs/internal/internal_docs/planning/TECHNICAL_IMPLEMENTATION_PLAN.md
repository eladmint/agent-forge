# Agent Forge Technical Implementation Plan

**Document Type:** Internal Technical Plan  
**Status:** Draft  
**Date:** June 2025  
**Confidentiality:** Internal Use Only

## Executive Summary

This document outlines the technical implementation strategy for Agent Forge's open source release, based on the architectural decisions documented in our ADRs. It covers repository restructuring, Steel Browser integration, CI/CD pipeline setup, and the infrastructure needed to support our open core monetization model.

## Implementation Overview

### **Phase 1: Repository Foundation (Weeks 1-4)**
- Monorepo structure implementation
- Steel Browser fork integration
- Apache 2.0 licensing application
- Basic CI/CD pipeline setup

### **Phase 2: Core Framework Preparation (Weeks 5-8)**
- Open source component isolation
- Premium feature gating system
- Documentation infrastructure
- Testing framework enhancement

### **Phase 3: Release Infrastructure (Weeks 9-12)**
- PyPI packaging and distribution
- Community infrastructure
- Monitoring and analytics
- Support systems

## Detailed Technical Implementation

### 1. Repository Structure Implementation

#### **Current State Analysis**
```
agent_forge/                    # Current structure
├── core/                      # Core framework components
├── examples/                  # Example agents (mix of open/premium)
├── docs/                      # Documentation
├── tests/                     # Test suites
└── requirements.txt           # Dependencies
```

#### **Target Monorepo Structure**
```
agent-forge/                   # New open source repository
├── libs/                      # Core libraries (open source)
│   ├── agent-forge-core/     
│   │   ├── __init__.py
│   │   ├── agents/           # BaseAgent, foundation classes
│   │   ├── config/           # Configuration management
│   │   ├── async_patterns/   # Async execution patterns
│   │   └── utilities/        # Core utilities
│   ├── agent-forge-web/      
│   │   ├── __init__.py
│   │   ├── browsers/         # Steel Browser integration
│   │   └── automation/       # Web automation utilities
│   ├── agent-forge-blockchain/
│   │   ├── __init__.py
│   │   ├── nmkr/            # NMKR integration
│   │   ├── masumi/          # Masumi integration
│   │   └── protocols/       # Blockchain protocols
│   └── agent-forge-community/
│       ├── __init__.py
│       ├── testing/         # Test utilities
│       └── tools/           # Development tools
├── examples/                  # Open source examples only
│   ├── basic/
│   │   ├── simple_navigation_agent.py
│   │   ├── text_extraction_agent.py
│   │   └── validation_agent.py
│   ├── intermediate/
│   │   ├── page_scraper_agent.py
│   │   └── data_compiler_agent.py
│   └── showcase/
│       └── agent_communication_hub.py
├── docs/                      # Public documentation
├── tests/                     # Comprehensive test suite
├── tools/                     # Build and development tools
├── external/                  # External dependencies
│   └── steel-browser-enhanced/ # Forked Steel Browser
├── .github/                   # GitHub configuration
│   ├── workflows/            # CI/CD workflows
│   ├── ISSUE_TEMPLATE/       # Issue templates
│   └── PULL_REQUEST_TEMPLATE.md
├── pyproject.toml            # Python project configuration
├── requirements.txt          # Core dependencies
├── LICENSE                   # Apache 2.0 license
├── README.md                 # Main documentation
├── CONTRIBUTING.md           # Contribution guidelines
├── SECURITY.md              # Security policy
└── CODE_OF_CONDUCT.md       # Community guidelines
```

#### **Migration Scripts**
```python
# scripts/migrate_to_monorepo.py
"""
Automated migration script to restructure current codebase
into open source monorepo format
"""

import shutil
import os
from pathlib import Path

def migrate_core_components():
    """Move core components to libs structure"""
    migrations = {
        "core/agents/": "libs/agent-forge-core/agents/",
        "core/shared/config/": "libs/agent-forge-core/config/",
        "core/shared/web/": "libs/agent-forge-web/browsers/",
        "core/blockchain/": "libs/agent-forge-blockchain/",
    }
    
    for source, target in migrations.items():
        migrate_directory(source, target)

def filter_examples():
    """Keep only open source examples"""
    open_source_examples = [
        "simple_navigation_agent.py",
        "text_extraction_agent.py", 
        "validation_agent.py",
        "page_scraper_agent.py",
        "data_compiler_agent.py",
        "agent_communication_hub.py"
    ]
    
    # Move premium examples to separate private repository
    # Keep only open source examples in public repo
```

### 2. Steel Browser Integration Strategy

#### **Fork Creation and Management**
```bash
# Initial fork setup
git clone https://github.com/steel-dev/steel-browser.git
cd steel-browser
git remote add agent-forge https://github.com/agent-forge/steel-browser-enhanced.git

# Create Agent Forge modifications branch
git checkout -b agent-forge-enhancements
```

#### **Integration Layer Implementation**
```python
# libs/agent-forge-web/browsers/steel_browser_client.py
"""
Agent Forge integration layer for Steel Browser
Provides simplified interface for AI agent workflows
"""

from typing import Optional, Dict, Any
import asyncio
from steel_browser import SteelBrowser
from ..config import BrowserConfig

class AgentForgeSteelClient:
    """
    Agent Forge wrapper for Steel Browser with AI-optimized features
    """
    
    def __init__(self, config: Optional[BrowserConfig] = None):
        self.config = config or BrowserConfig()
        self._browser: Optional[SteelBrowser] = None
        
    async def create_session(self) -> SteelBrowser:
        """Create optimized browser session for AI agents"""
        if not self._browser:
            self._browser = SteelBrowser(
                api_key=self.config.api_key,
                # Agent Forge optimizations
                wait_for_navigation=True,
                auto_wait_for_content=True,
                ai_extraction_mode=True,  # Our custom enhancement
            )
        return self._browser
        
    async def extract_structured_data(self, url: str, schema: Dict) -> Dict[str, Any]:
        """AI-powered structured data extraction"""
        browser = await self.create_session()
        
        # Navigate and wait for content
        await browser.go(url)
        await browser.wait_for_load_state("domcontentloaded")
        
        # Apply our AI extraction enhancements
        return await browser.extract_data_with_ai_schema(schema)
```

#### **Modification Tracking System**
```python
# external/steel-browser-enhanced/AGENT_FORGE_MODIFICATIONS.md
"""
# Agent Forge Modifications to Steel Browser

## Summary
This document tracks all modifications made to Steel Browser for Agent Forge integration.

## Modifications

### 1. AI-Optimized Content Waiting
**File**: `src/browser/page.py`
**Lines**: 245-267
**Change**: Added intelligent content waiting for AI extraction
**Rationale**: Improves reliability for AI agent workflows

### 2. Enhanced Error Handling  
**File**: `src/browser/errors.py`
**Lines**: 89-112
**Change**: Added Agent Forge specific error types
**Rationale**: Better debugging for agent developers

## Sync Status
**Last Upstream Sync**: 2025-06-01
**Next Scheduled Sync**: 2025-07-01
**Security Updates**: Up to date as of 2025-06-01
"""
```

### 3. Premium Feature Gating System

#### **Tier Management Infrastructure**
```python
# libs/agent-forge-core/licensing/tier_manager.py
"""
Tier-based feature access control for open core model
"""

from enum import Enum
from typing import Optional, Callable
import os
import requests
from functools import wraps

class AgentForgeTier(Enum):
    COMMUNITY = "community"
    PROFESSIONAL = "professional"  
    ENTERPRISE = "enterprise"
    STRATEGIC = "strategic"

class LicenseManager:
    """Manages license validation and tier access"""
    
    def __init__(self):
        self.api_key = os.getenv("AGENT_FORGE_API_KEY")
        self.current_tier = self._detect_tier()
        
    def _detect_tier(self) -> AgentForgeTier:
        """Detect current license tier"""
        if not self.api_key:
            return AgentForgeTier.COMMUNITY
            
        # Validate with license server
        response = requests.get(
            "https://api.agentforge.dev/v1/license/validate",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        
        if response.status_code == 200:
            tier_name = response.json().get("tier", "community")
            return AgentForgeTier(tier_name)
        
        return AgentForgeTier.COMMUNITY

def requires_tier(required_tier: AgentForgeTier):
    """Decorator for tier-gated features"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            license_manager = LicenseManager()
            
            if not license_manager.has_access(required_tier):
                raise PermissionError(
                    f"This feature requires {required_tier.value} tier. "
                    f"Current tier: {license_manager.current_tier.value}. "
                    f"Upgrade at https://agentforge.dev/pricing"
                )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage example
@requires_tier(AgentForgeTier.PROFESSIONAL)
def load_premium_examples():
    """Load premium example agents"""
    # Implementation for premium examples
    pass
```

#### **Open Source Component Isolation**
```python
# libs/agent-forge-core/examples/community_examples.py
"""
Community tier examples - always available in open source
"""

COMMUNITY_EXAMPLES = {
    "simple_navigation": {
        "name": "Simple Navigation Agent",
        "description": "Basic web navigation and interaction",
        "file": "examples/basic/simple_navigation_agent.py",
        "tier": "community"
    },
    "text_extraction": {
        "name": "Text Extraction Agent", 
        "description": "Extract text content from web pages",
        "file": "examples/basic/text_extraction_agent.py",
        "tier": "community"
    },
    "validation": {
        "name": "Validation Agent",
        "description": "Validate data and forms",
        "file": "examples/basic/validation_agent.py", 
        "tier": "community"
    }
}

# Premium examples would be in separate private repository
# with tier gating when accessed
```

### 4. CI/CD Pipeline Implementation

#### **GitHub Actions Workflow**
```yaml
# .github/workflows/ci.yml
name: Agent Forge CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]
        
    steps:
    - uses: actions/checkout@v4
      with:
        submodules: recursive  # For Steel Browser fork
        
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev,test]
        
    - name: Lint code
      run: |
        flake8 libs/ examples/ tests/
        black --check libs/ examples/ tests/
        isort --check-only libs/ examples/ tests/
        
    - name: Security scan
      run: |
        safety check
        bandit -r libs/
        
    - name: Run tests
      run: |
        pytest tests/ --cov=libs --cov-report=xml
        
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.9
        
    - name: Build package
      run: |
        python -m build
        
    - name: Test installation
      run: |
        pip install dist/*.whl
        python -c "import agent_forge; print('Import successful')"

  security:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'
        
    - name: Upload Trivy scan results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'
```

#### **Smart Testing Strategy**
```python
# tools/ci/smart_test.py
"""
Smart testing that only runs tests for changed components
"""

import subprocess
import sys
from pathlib import Path

def get_changed_files():
    """Get list of changed files from git"""
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD^", "HEAD"],
        capture_output=True, text=True
    )
    return result.stdout.strip().split('\n')

def determine_test_scope(changed_files):
    """Determine which test suites to run based on changes"""
    test_scope = set()
    
    for file_path in changed_files:
        if file_path.startswith("libs/agent-forge-core/"):
            test_scope.add("tests/unit/core/")
        elif file_path.startswith("libs/agent-forge-web/"):
            test_scope.add("tests/unit/web/")
            test_scope.add("tests/integration/browser/")
        elif file_path.startswith("libs/agent-forge-blockchain/"):
            test_scope.add("tests/unit/blockchain/")
        elif file_path.startswith("examples/"):
            test_scope.add("tests/e2e/examples/")
        elif file_path.startswith("docs/"):
            test_scope.add("tests/docs/")
            
    # Always run core integration tests
    test_scope.add("tests/integration/core/")
    
    return list(test_scope)

if __name__ == "__main__":
    changed_files = get_changed_files()
    test_paths = determine_test_scope(changed_files)
    
    if test_paths:
        cmd = ["pytest"] + test_paths + ["--cov=libs", "--cov-report=xml"]
        sys.exit(subprocess.call(cmd))
    else:
        print("No tests needed for changes")
        sys.exit(0)
```

### 5. Package Distribution Strategy

#### **PyPI Configuration**
```toml
# pyproject.toml
[build-system]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"

[project]
name = "agent-forge"
dynamic = ["version"]
description = "Production-ready Python framework for AI web agents"
readme = "README.md"
license = "Apache-2.0"
authors = [
    {name = "Agent Forge Contributors", email = "contributors@agentforge.dev"},
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9", 
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Internet :: WWW/HTTP :: Browsers",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
]
keywords = ["ai", "agents", "automation", "web-scraping", "blockchain"]
dependencies = [
    "steel-browser>=1.0.0",
    "asyncio-mqtt>=0.11.0",
    "pydantic>=2.0.0",
    "httpx>=0.24.0",
    "beautifulsoup4>=4.11.0",
    "python-dotenv>=1.0.0",
]
requires-python = ">=3.8"

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "isort>=5.11.0",
    "safety>=2.3.0",
    "bandit>=1.7.0",
]
blockchain = [
    "web3>=6.0.0",
    "eth-account>=0.8.0",
]
enterprise = [
    "redis>=4.5.0",
    "celery>=5.2.0",
    "prometheus-client>=0.16.0",
]

[project.urls]
Homepage = "https://agentforge.dev"
Documentation = "https://docs.agentforge.dev"
Repository = "https://github.com/agent-forge/agent-forge"
"Bug Tracker" = "https://github.com/agent-forge/agent-forge/issues"

[project.scripts]
agent-forge = "agent_forge.cli:main"

[tool.hatch.version]
source = "vcs"

[tool.hatch.build.targets.wheel]
packages = ["libs/agent-forge-core/src/agent_forge"]
```

#### **Automated Release Workflow**
```yaml
# .github/workflows/release.yml
name: Release to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: release
    permissions:
      id-token: write  # For trusted publishing
      
    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0  # Full history for version tagging
        
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.9
        
    - name: Install build dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
        
    - name: Build package
      run: python -m build
      
    - name: Check package
      run: twine check dist/*
      
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        repository-url: https://upload.pypi.org/legacy/
```

### 6. Documentation Infrastructure

#### **Documentation Site Setup**
```python
# docs/conf.py - Sphinx configuration
"""
Sphinx configuration for Agent Forge documentation
"""

import os
import sys
sys.path.insert(0, os.path.abspath('../libs'))

project = 'Agent Forge'
copyright = '2025, Agent Forge Contributors'
author = 'Agent Forge Contributors'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx_rtd_theme',
    'myst_parser',
]

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Auto-generate API documentation
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
}
```

#### **API Reference Generation**
```bash
# tools/docs/generate_api_docs.sh
#!/bin/bash
"""
Automated API documentation generation
"""

# Generate API documentation from docstrings
sphinx-apidoc -o docs/api/ libs/ --force --module-first

# Build documentation
cd docs/
make clean
make html

# Deploy to GitHub Pages (in CI)
if [ "$GITHUB_ACTIONS" = "true" ]; then
    cd _build/html/
    touch .nojekyll
    git init
    git add -A
    git commit -m "Deploy documentation"
    git push -f https://github.com/agent-forge/agent-forge.git main:gh-pages
fi
```

### 7. Community Infrastructure Setup

#### **GitHub Repository Configuration**
```yaml
# .github/ISSUE_TEMPLATE/bug_report.yml
name: Bug Report
description: Report a bug in Agent Forge
title: "[Bug]: "
labels: ["bug", "triage"]

body:
  - type: markdown
    attributes:
      value: |
        Thanks for taking the time to report a bug! Please fill out the sections below.
        
  - type: input
    id: version
    attributes:
      label: Agent Forge Version
      description: What version of Agent Forge are you using?
      placeholder: e.g., 1.0.0
    validations:
      required: true
      
  - type: textarea
    id: description
    attributes:
      label: Bug Description
      description: A clear and concise description of the bug
      placeholder: Describe what happened and what you expected
    validations:
      required: true
      
  - type: textarea
    id: reproduction
    attributes:
      label: Steps to Reproduce
      description: Steps to reproduce the behavior
      placeholder: |
        1. Go to '...'
        2. Click on '....'
        3. Scroll down to '....'
        4. See error
    validations:
      required: true
      
  - type: textarea
    id: environment
    attributes:
      label: Environment
      description: |
        Please provide information about your environment:
        - OS: [e.g. Ubuntu 20.04, macOS 12.0, Windows 11]
        - Python version: [e.g. 3.9.0]
        - Browser: [if applicable]
      placeholder: Environment details
    validations:
      required: true
```

#### **Community Guidelines**
```markdown
# CODE_OF_CONDUCT.md
# Agent Forge Community Code of Conduct

## Our Pledge

We as members, contributors, and leaders pledge to make participation in our
community a harassment-free experience for everyone, regardless of age, body
size, visible or invisible disability, ethnicity, sex characteristics, gender
identity and expression, level of experience, education, socio-economic status,
nationality, personal appearance, race, caste, color, religion, or sexual
identity and orientation.

## Our Standards

Examples of behavior that contributes to a positive environment:

* Demonstrating empathy and kindness toward other people
* Being respectful of differing opinions, viewpoints, and experiences
* Giving and gracefully accepting constructive feedback
* Accepting responsibility and apologizing to those affected by our mistakes
* Focusing on what is best not just for us as individuals, but for the overall community

## Enforcement

Community leaders are responsible for clarifying and enforcing our standards of
acceptable behavior and will take appropriate and fair corrective action in
response to any behavior that they deem inappropriate, threatening, offensive,
or harmful.

For questions or concerns, contact: community@agentforge.dev
```

## Implementation Timeline

### **Week 1-2: Repository Foundation**
- [ ] Create new monorepo structure
- [ ] Migrate current codebase using automated scripts
- [ ] Set up Steel Browser fork with modifications tracking
- [ ] Apply Apache 2.0 licensing to all files

### **Week 3-4: CI/CD & Testing**
- [ ] Implement GitHub Actions workflows
- [ ] Set up smart testing system
- [ ] Configure security scanning and dependency monitoring
- [ ] Establish PyPI trusted publishing

### **Week 5-6: Feature Gating & Documentation**
- [ ] Implement tier management system
- [ ] Set up premium feature gating
- [ ] Configure documentation generation
- [ ] Create API reference documentation

### **Week 7-8: Community Infrastructure**
- [ ] Set up GitHub issue templates and PR templates
- [ ] Create community guidelines and contribution docs
- [ ] Configure Discord/forum integration
- [ ] Implement analytics and monitoring

## Success Criteria

- [ ] **Repository Setup**: All code migrated to monorepo structure
- [ ] **CI/CD**: All tests passing, <10 minute build time
- [ ] **Documentation**: Complete API reference, getting started guide
- [ ] **Community**: Issue templates, contribution guidelines, code of conduct
- [ ] **Legal Compliance**: All files properly licensed, attribution complete
- [ ] **Feature Gating**: Tier system functional, premium features gated
- [ ] **Steel Browser**: Fork properly integrated with modification tracking

## Risk Mitigation

### **Technical Risks**
- **Migration Issues**: Comprehensive testing in staging environment
- **Steel Browser Integration**: Fallback to reference implementation if fork fails
- **Performance Degradation**: Benchmarking before/after migration

### **Legal Risks**
- **Licensing Conflicts**: Legal review before any code publication
- **Attribution Issues**: Automated compliance checking in CI

### **Community Risks**
- **Poor Reception**: Beta testing with select developers first
- **Support Overwhelm**: Clear community guidelines and automated responses

---

**Next Steps**: Begin implementation with repository foundation setup and automated migration scripts.

**Review Required**: Technical approach validation with team before proceeding.

**Documentation Dependencies**: This plan references ADRs 001-006 for strategic context.
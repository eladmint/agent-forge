# ADR-004: Repository Structure - Monorepo vs Multi-repo

**Status**: Accepted  
**Date**: 2025-06-14  
**Deciders**: Agent Forge Technical Team  
**Technical Story**: Open Source Repository Organization Strategy

## Context and Problem Statement

Agent Forge consists of multiple components: core framework, browser integration, blockchain integrations, examples, and documentation. For open source release, we need to decide between organizing these as a single monorepo or multiple separate repositories. This decision impacts developer experience, contribution management, CI/CD complexity, and release coordination.

## Decision Drivers

- **Developer Experience**: Easy setup, clear navigation, and minimal complexity
- **Contribution Management**: Streamlined process for community contributions
- **Release Coordination**: Ability to coordinate releases across components
- **Dependency Management**: Clear dependency relationships and versioning
- **CI/CD Efficiency**: Build times, testing strategy, and deployment coordination
- **Community Growth**: Structure that encourages exploration and contribution

## Considered Options

### Option 1: Monorepo Structure
- Single repository containing all Agent Forge components
- Unified versioning and release process
- Shared tooling and CI/CD pipeline
- Clear component boundaries within single repo

### Option 2: Multi-repo Structure
- Separate repositories for core, integrations, examples, and docs
- Independent versioning and release cycles
- Specialized CI/CD for each component
- Cross-repository dependency management

### Option 3: Hybrid Structure
- Core framework as main repository
- Separate repositories for major integrations
- Examples and docs as part of main repository

## Decision Outcome

**Chosen Option**: **Monorepo Structure (Option 1)**

### Repository Organization:
```
agent-forge/
├── libs/                           # Core libraries
│   ├── agent-forge-core/          # BaseAgent, async patterns, config
│   ├── agent-forge-web/           # Browser automation integration
│   ├── agent-forge-blockchain/    # NMKR, Masumi integrations
│   └── agent-forge-community/     # Community tools and utilities
├── examples/                      # Example agents (basic open source set)
│   ├── basic/                     # Simple examples for learning
│   ├── intermediate/              # More complex examples
│   └── showcase/                  # Production-ready showcases
├── docs/                          # Public documentation
│   ├── api/                       # API reference
│   ├── guides/                    # User guides and tutorials
│   ├── integrations/              # Integration documentation
│   └── architecture/              # Technical architecture docs
├── tests/                         # Test suites
│   ├── unit/                      # Unit tests for all components
│   ├── integration/               # Integration tests
│   ├── e2e/                       # End-to-end tests
│   └── performance/               # Performance and load tests
├── tools/                         # Development and build tools
│   ├── build/                     # Build scripts and configuration
│   ├── ci/                        # CI/CD utilities
│   └── dev/                       # Development utilities
├── external/                      # External dependencies (Steel Browser fork)
├── requirements.txt               # Unified dependency management
├── pyproject.toml                # Python project configuration
├── LICENSE                       # Apache 2.0 license
├── README.md                     # Main project documentation
└── CONTRIBUTING.md               # Contribution guidelines
```

## Positive Consequences

- **Unified Experience**: Single `git clone` gets everything working
- **Atomic Changes**: Cross-component changes in single commits/PRs
- **Simplified CI/CD**: Single pipeline for all components with shared tooling
- **Consistent Tooling**: Unified linting, testing, and build processes
- **Easy Discovery**: Users can explore all capabilities in one place
- **Reduced Overhead**: Single issue tracker, unified documentation, shared configurations

## Negative Consequences

- **Repository Size**: Larger repository may be intimidating to new contributors
- **Build Complexity**: CI/CD needs to handle multiple component types
- **Permission Granularity**: Cannot set different permissions per component
- **Release Coupling**: All components released together

### Mitigation Strategies

- **Clear Documentation**: Comprehensive navigation and getting started guides
- **Selective CI**: Smart CI that only builds/tests changed components
- **Component Independence**: Clear boundaries and minimal coupling between components
- **Progressive Disclosure**: Documentation structure that guides users from simple to complex

## Pros and Cons of the Options

### Monorepo Structure
**Pros:**
- Single source of truth for entire framework
- Atomic cross-component changes
- Unified tooling and CI/CD
- Easier dependency management
- Better developer onboarding experience
- Simplified issue tracking and project management

**Cons:**
- Larger repository size
- More complex CI/CD logic
- All components share same release cycle
- Cannot set granular permissions
- Potential for tighter coupling between components

### Multi-repo Structure
**Pros:**
- Independent release cycles
- Specialized CI/CD per component
- Granular access control
- Smaller, focused repositories
- Clear separation of concerns
- Independent community management

**Cons:**
- Complex cross-repository coordination
- Dependency management overhead
- Multiple places for issues/PRs
- Harder to discover all capabilities
- Risk of version conflicts
- More administrative overhead

### Hybrid Structure
**Pros:**
- Balance between unified and independent
- Core framework can evolve independently
- Specialized repositories for complex integrations
- Flexibility in versioning strategies

**Cons:**
- Most complex option to manage
- Unclear boundaries for what goes where
- Dependency coordination still required
- Multiple issue trackers and communities
- Inconsistent developer experience

## Technical Implementation Details

### Build System
- **Poetry/pip-tools**: Unified dependency management with lock files
- **pytest**: Comprehensive testing framework across all components
- **pre-commit**: Unified code quality and formatting
- **GitHub Actions**: Smart CI that detects changes and runs appropriate tests

### Component Architecture
- **Independent Modules**: Each lib can be imported independently
- **Clear Interfaces**: Well-defined APIs between components
- **Optional Dependencies**: Core framework works without all integrations
- **Plugin Architecture**: Extensions can be added without core changes

### Development Workflow
```bash
# Clone and setup
git clone https://github.com/agent-forge/agent-forge.git
cd agent-forge
pip install -e .[dev]  # Install all components in development mode

# Work on specific component
cd libs/agent-forge-core
# Make changes, tests are co-located

# Run tests for specific component
pytest tests/unit/core/

# Run all tests
pytest

# Run only changed component tests (CI optimization)
python tools/ci/smart_test.py
```

### Release Process
- **Unified Versioning**: Single version number for entire framework
- **Component Compatibility**: Clear compatibility matrix between component versions  
- **Semantic Versioning**: Major.minor.patch with clear breaking change policy
- **Release Notes**: Comprehensive notes covering all component changes

## Performance Considerations

### CI/CD Optimization
- **Change Detection**: Only build/test components that changed
- **Parallel Execution**: Run independent test suites in parallel
- **Caching Strategy**: Aggressive caching of dependencies and build artifacts
- **Smart Matrix**: Dynamic test matrix based on changed components

### Developer Experience
- **Selective Installation**: `pip install agent-forge[core]` for minimal install
- **Development Mode**: Fast iteration with `pip install -e .`
- **Documentation Generation**: Auto-generated docs from monorepo source
- **IDE Support**: Clear project structure for IDEs to understand

## Security Considerations

- **Dependency Scanning**: Unified security scanning across all components
- **Access Control**: Repository-level access control for entire framework
- **Secret Management**: Centralized secret management for CI/CD
- **Audit Trail**: Single location for all security-related changes

## Success Metrics

- **Setup Time**: <5 minutes from clone to working development environment
- **CI Performance**: <10 minutes for full test suite
- **Contribution Rate**: Increased PR rate due to simplified contribution process
- **Issue Management**: <24 hour response time with unified issue tracking
- **Documentation Quality**: Single source of truth improves docs consistency

## Links

- [Monorepo Best Practices](https://monorepo.tools/)
- [LangChain Repository Structure](https://github.com/langchain-ai/langchain)
- [Google Monorepo Paper](https://cacm.acm.org/magazines/2016/7/204032-why-google-stores-billions-of-lines-of-code-in-a-single-repository/fulltext)
- [Nx Monorepo Tools](https://nx.dev/)
- [Python Project Structure Best Practices](https://docs.python-guide.org/writing/structure/)
- [GitHub Actions Monorepo CI](https://docs.github.com/en/actions/using-workflows/using-github-actions-for-continuous-integration)
- [Poetry Dependency Management](https://python-poetry.org/docs/)
- [pytest Testing Framework](https://docs.pytest.org/)
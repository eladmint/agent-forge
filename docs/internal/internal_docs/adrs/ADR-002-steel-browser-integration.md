# ADR-002: Steel Browser Integration Strategy

**Status**: Accepted  
**Date**: 2025-06-14  
**Deciders**: Agent Forge Technical Team  
**Technical Story**: External Dependency Management for Open Source Release

## Context and Problem Statement

Agent Forge has significant customizations to Steel Browser (https://github.com/steel-dev/steel-browser) for AI agent workflows. For open source release, we need to decide how to handle this dependency: reference the original repository, fork and maintain our modifications, or include the modified version directly.

## Decision Drivers

- **User Experience**: Developers should have seamless setup and functionality
- **Maintenance Burden**: Must be sustainable for small team to maintain
- **Legal Compliance**: Must respect Steel Browser's licensing terms
- **Innovation Speed**: Enable rapid iteration on browser automation features
- **Community Benefit**: Approach should benefit both Agent Forge and Steel Browser communities

## Considered Options

### Option 1: Reference Original Repository
- Point to original Steel Browser repository
- Document required modifications in setup guide
- Users apply modifications themselves or use compatibility layer

### Option 2: Fork with Attribution
- Create `agent-forge/steel-browser-enhanced` fork
- Maintain our modifications with clear attribution
- Periodically sync critical updates from upstream

### Option 3: Include Modified Version
- Bundle modified Steel Browser directly in Agent Forge repository
- Full control over modifications and versions
- No external dependencies for users

## Decision Outcome

**Chosen Option**: **Fork with Attribution (Option 2)**

### Implementation Approach:

1. **Create Fork**: `agent-forge/steel-browser-enhanced`
2. **Attribution**: Clear documentation crediting original Steel Browser project
3. **Modification Tracking**: Comprehensive changelog of all customizations
4. **Upstream Sync**: Regular review and integration of critical upstream updates
5. **Contribution**: Offer beneficial modifications back to upstream when appropriate

### Repository Structure:
```
agent-forge/
├── core/
│   └── web/
│       └── browsers/
│           └── steel_browser_client.py  # Integration layer
├── external/
│   └── steel-browser-enhanced/          # Forked repository as submodule
└── docs/
    └── integrations/
        └── STEEL_BROWSER_INTEGRATION.md # Attribution and modifications
```

## Positive Consequences

- **Seamless User Experience**: Users get working browser automation without additional setup
- **Controlled Evolution**: Can iterate quickly on AI-specific browser features
- **Legal Compliance**: Proper attribution respects original project's contributions
- **Maintainable**: Clear separation between core framework and browser functionality
- **Community Benefit**: Potential to contribute improvements back to Steel Browser

## Negative Consequences

- **Maintenance Overhead**: Responsibility for maintaining fork and tracking upstream
- **Potential Divergence**: Risk of growing incompatibility with upstream
- **Resource Requirements**: Team time needed for fork maintenance and updates
- **Community Perception**: May be viewed as fragmenting the browser automation ecosystem

### Mitigation Strategies

- **Automated Sync Checks**: Regular automated checks for upstream security updates
- **Minimal Modifications**: Keep customizations focused and well-documented
- **Upstream Engagement**: Active participation in Steel Browser community
- **Clear Documentation**: Transparent communication about modifications and rationale

## Pros and Cons of the Options

### Reference Original Repository
**Pros:**
- No maintenance burden for Agent Forge team
- Users benefit from all upstream improvements automatically
- Respects original project without modification
- Simplest legal and ethical approach

**Cons:**
- Poor user experience requiring manual modifications
- May break when upstream changes conflict with our requirements
- Difficult to provide reliable support
- Limits innovation in browser automation features

### Fork with Attribution
**Pros:**
- Complete control over browser automation functionality
- Seamless user experience with working setup
- Ability to innovate quickly on AI-specific features
- Proper attribution maintains community relationships
- Option to contribute back valuable improvements

**Cons:**
- Ongoing maintenance responsibility
- Risk of divergence from upstream
- Resource allocation for fork management
- Potential community fragmentation

### Include Modified Version
**Pros:**
- Simplest for users - no external dependencies
- Complete control over all code
- No risk of upstream breaking changes
- Fastest setup and deployment

**Cons:**
- Significant maintenance burden for entire browser codebase
- Legal complexity of bundling large external project
- Difficult to benefit from upstream improvements
- May be seen as appropriating rather than collaborating

## Technical Implementation Details

### Fork Management Process

1. **Initial Fork Creation**
   ```bash
   git clone https://github.com/steel-dev/steel-browser.git
   cd steel-browser
   git remote add agent-forge https://github.com/agent-forge/steel-browser-enhanced.git
   ```

2. **Modification Tracking**
   - All Agent Forge modifications tagged with `[AGENT-FORGE]` comments
   - Comprehensive `MODIFICATIONS.md` file documenting all changes
   - Git commits clearly marked as Agent Forge customizations

3. **Upstream Sync Process**
   ```bash
   # Monthly upstream sync
   git fetch upstream
   git checkout main
   git merge upstream/main
   # Resolve conflicts, test, and update MODIFICATIONS.md
   ```

4. **Integration Layer**
   - `steel_browser_client.py` provides Agent Forge-specific interface
   - Isolates core framework from browser implementation details
   - Enables future browser engine swapping if needed

### Attribution Requirements

- **README**: Prominent attribution to Steel Browser project
- **LICENSE**: Include Steel Browser license alongside Agent Forge license  
- **Documentation**: Clear explanation of relationship and modifications
- **Code Comments**: Attribution comments in modified source files

## Security Considerations

- **Dependency Scanning**: Regular security scans of forked repository
- **Upstream Security Updates**: Priority process for integrating security patches
- **Isolated Execution**: Browser processes run in sandboxed environment
- **Access Controls**: Limited network and filesystem access for browser automation

## Success Metrics

- **Maintenance Effort**: <4 hours/month for fork maintenance
- **User Satisfaction**: <5 setup-related support tickets/month
- **Upstream Relationship**: Regular communication with Steel Browser maintainers
- **Contribution Rate**: At least 1 upstream contribution per quarter

## Links

- [Steel Browser Original Repository](https://github.com/steel-dev/steel-browser)
- [Agent Forge Browser Integration Docs](../../docs/integrations/STEEL_BROWSER_INTEGRATION.md)
- [Open Source Dependency Management Best Practices](../research/AI_OPEN_SOURCE_BEST_PRACTICES.md)
- [Fork Maintenance Guidelines](https://docs.github.com/en/github/collaborating-with-pull-requests/working-with-forks)
- [Open Source Attribution Guidelines](https://opensource.guide/legal/)
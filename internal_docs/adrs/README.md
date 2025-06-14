# Open Source Release ADRs

This directory contains Architectural Decision Records (ADRs) specifically for Agent Forge's open source release strategy and implementation decisions.

**⚠️ Note**: These are internal planning ADRs separate from the main project's service-aligned ADR organization.

## ADR Index

### Strategic Decisions
- **[ADR-001: Open Core vs Full Open Source Model](./ADR-001-open-core-model.md)** ✅
- **[ADR-002: Steel Browser Integration Strategy](./ADR-002-steel-browser-integration.md)** ✅  
- **[ADR-003: Licensing Strategy - Apache 2.0 vs MIT](./ADR-003-licensing-strategy.md)** ✅
- **[ADR-004: Repository Structure - Monorepo vs Multi-repo](./ADR-004-repository-structure.md)** ✅
- **[ADR-005: Monetization Tier Structure](./ADR-005-monetization-tiers.md)** ✅
- **[ADR-006: Release Timeline and Phases](./ADR-006-release-timeline.md)** ✅

### Technical Decisions (Planned)
- **ADR-007**: [Quality Assurance Framework](./ADR-007-quality-assurance.md)
- **ADR-008**: [CI/CD Pipeline for Open Source](./ADR-008-cicd-pipeline.md)
- **ADR-009**: [Documentation Architecture](./ADR-009-documentation-architecture.md)
- **ADR-010**: [Security and Compliance Framework](./ADR-010-security-framework.md)

### Release Management (Planned)
- **ADR-011**: [Community Building Strategy](./ADR-011-community-strategy.md)
- **ADR-012**: [Partnership and Ecosystem Strategy](./ADR-012-partnership-strategy.md)

## Key Decisions Summary

### **Open Core Strategy** (ADR-001)
- Core framework open source (Apache 2.0)
- Premium examples and enterprise features commercial
- Multi-tier monetization: Community → Professional ($99) → Enterprise ($999) → Strategic

### **Steel Browser Approach** (ADR-002)  
- Fork with attribution for seamless user experience
- Maintain modifications with upstream sync process
- Clear documentation of customizations and rationale

### **Technical Foundation** (ADR-003, ADR-004)
- Apache 2.0 licensing for patent protection and enterprise acceptance
- Monorepo structure for simplified developer experience
- Unified CI/CD and dependency management

### **Revenue Model** (ADR-005)
- Target: $50K → $250K → $1M ARR over 3 years
- Freemium conversion rate: 3-4% industry standard
- Premium marketplace for community monetization

### **Launch Timeline** (ADR-006)
- 12-week phased rollout: Foundation → Beta → Launch → Scale
- Risk-managed approach with quality gates
- Beta testing with 25-50 experienced developers

## ADR Template

```markdown
# ADR-XXX: [Title]

**Status**: [Proposed/Accepted/Deprecated/Superseded]  
**Date**: [YYYY-MM-DD]  
**Deciders**: [List of people involved]  
**Technical Story**: [Context/ticket reference]

## Context and Problem Statement
## Decision Drivers  
## Considered Options
## Decision Outcome
## Positive Consequences
## Negative Consequences
## Links
```

## Related Documentation

- **Strategy**: [Open Source Release Strategy](../strategy/OPEN_SOURCE_RELEASE_STRATEGY.md)
- **Research**: [Competitive Analysis](../research/AI_FRAMEWORK_COMPETITIVE_ANALYSIS.md)
- **Research**: [Monetization Strategies](../research/MONETIZATION_STRATEGIES_FOR_OPEN_SOURCE.md)
- **Main Project ADRs**: `../../memory-bank/adrs/` (service-aligned organization)

---

*These ADRs focus specifically on open source release decisions and complement the main project's service-aligned ADR structure.* 
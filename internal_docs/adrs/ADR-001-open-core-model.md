# ADR-001: Open Core vs Full Open Source Model

**Status**: Accepted  
**Date**: 2025-06-14  
**Deciders**: Agent Forge Release Team  
**Technical Story**: Open Source Release Strategy

## Context and Problem Statement

Agent Forge is ready for open source release with a production-ready framework, comprehensive examples, and enterprise integrations. We need to decide between releasing everything as open source vs. adopting an open core model that enables sustainable business development.

## Decision Drivers

- **Sustainability**: Need sustainable revenue model for long-term development
- **Adoption**: Maximize developer adoption and community growth
- **Competition**: AI framework market is crowded (LangChain 90K stars, CrewAI $18M funding)
- **Value Differentiation**: Premium features must justify commercial pricing
- **Community Trust**: Balance between open source values and business needs

## Considered Options

### Option 1: Full Open Source
- Release everything under permissive license (MIT/Apache 2.0)
- Monetize through services, consulting, and hosted solutions only
- Rely on community donations and sponsorships

### Option 2: Open Core Model
- Release core framework as open source
- Keep premium examples and enterprise features commercial
- Freemium model with conversion to paid tiers

### Option 3: Dual Licensing
- Offer both open source and commercial licenses
- Open source for community use, commercial for enterprise
- Complex licensing management

## Decision Outcome

**Chosen Option**: **Open Core Model (Option 2)**

### Core Components (Open Source):
- ✅ BaseAgent foundation and async patterns
- ✅ Configuration management with security validation
- ✅ Steel Browser integration layer
- ✅ Basic documentation and getting started guides
- ✅ Core testing framework and utilities

### Premium Components (Commercial):
- 💰 Advanced example agents (token research, social media, blockchain)
- 💰 Enterprise features (monitoring, compliance, multi-tenancy)
- 💰 Hosted services and managed deployment
- 💰 Professional services and custom development
- 💰 Priority support and SLA guarantees

## Positive Consequences

- **Sustainable Revenue**: Multiple revenue streams support long-term development
- **Community Growth**: Free core enables broad adoption and community building
- **Competitive Position**: Aligns with successful frameworks (LangChain, CrewAI)
- **Value Clarity**: Clear distinction between community and commercial value
- **Development Focus**: Revenue funds continued innovation and improvements

## Negative Consequences

- **Community Perception**: Risk of being seen as "not truly open source"
- **Complexity**: Managing multiple tiers and licensing requires overhead
- **Competition**: Premium features may be replicated by competitors
- **Maintenance**: Supporting both open and commercial versions

### Mitigation Strategies

- **Transparent Communication**: Clear documentation of what's open vs. premium
- **Community Value**: Ensure open source core provides genuine value
- **Regular Contributions**: Continuously improve open source components
- **Fair Pricing**: Reasonable pricing that reflects value delivered

## Pros and Cons of the Options

### Full Open Source
**Pros:**
- Maximum community trust and adoption
- Simplified licensing and legal structure
- Potential for rapid community contributions
- Clear competitive advantage in "truly open" positioning

**Cons:**
- Limited revenue opportunities
- Dependency on donations/sponsorships
- Difficulty funding long-term development
- Risk of commercial exploitation without contribution

### Open Core Model
**Pros:**
- Sustainable business model proven by industry leaders
- Attracts enterprise customers while maintaining community
- Funds continued development and innovation
- Clear value differentiation

**Cons:**
- Requires careful balance between open and commercial features
- Potential community backlash if not handled transparently
- Complex licensing and tier management
- Risk of feature creep into commercial tier

### Dual Licensing
**Pros:**
- Flexible licensing options for different use cases
- Clear commercial path for enterprise customers
- Maintains open source community benefits

**Cons:**
- Complex legal structure and management
- Potential confusion for users
- Requires sophisticated licensing infrastructure
- May limit community contributions

## Implementation Guidelines

### Open Source Core Principles
1. **Genuine Value**: Open source core must provide real, production-ready value
2. **Clear Boundaries**: Transparent documentation of what's included/excluded
3. **Community Focus**: Regular improvements and features for open source tier
4. **No Artificial Limits**: Avoid crippling open source version to drive sales

### Commercial Tier Principles
1. **Value Addition**: Premium features must provide clear, additional value
2. **Enterprise Focus**: Target enterprise-specific needs (compliance, support, scale)
3. **Fair Pricing**: Pricing reflects value delivered, not artificial scarcity
4. **Customer Success**: Ensure commercial customers achieve their goals

## Links

- [Open Source Release Strategy](../strategy/OPEN_SOURCE_RELEASE_STRATEGY.md)
- [Monetization Strategy Research](../research/MONETIZATION_STRATEGIES_FOR_OPEN_SOURCE.md)
- [Competitive Analysis](../research/AI_FRAMEWORK_COMPETITIVE_ANALYSIS.md)
- [LangChain Business Model](https://blog.langchain.dev/langchain-business-model/)
- [Open Core Model Analysis](https://a16z.com/2020/02/19/open-source-business-models-open-core/)
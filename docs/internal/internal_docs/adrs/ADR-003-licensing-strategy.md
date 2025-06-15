# ADR-003: Licensing Strategy - Apache 2.0 vs MIT

**Status**: Accepted  
**Date**: 2025-06-14  
**Deciders**: Agent Forge Legal & Technical Team  
**Technical Story**: Open Source License Selection for Framework Release

## Context and Problem Statement

Agent Forge requires an open source license for the core framework release. The choice impacts enterprise adoption, contributor protection, patent considerations, and compatibility with existing dependencies. We need to select the optimal license that balances openness, enterprise acceptance, and legal protection.

## Decision Drivers

- **Enterprise Adoption**: License must be acceptable to enterprise customers
- **Patent Protection**: Framework includes AI/automation innovations that may have patent implications
- **Contributor Protection**: Need legal protection for contributors and maintainers
- **Ecosystem Compatibility**: Must be compatible with Steel Browser and other dependencies
- **Community Trust**: License should align with open source community expectations
- **Commercial Flexibility**: Must support our open core business model

## Considered Options

### Option 1: MIT License
- Most permissive license with minimal restrictions
- Maximum compatibility and enterprise acceptance
- No explicit patent grant
- Simple, well-understood terms

### Option 2: Apache 2.0 License
- Permissive license with explicit patent grant
- Strong contributor and user protection
- Widely accepted by enterprises
- More comprehensive legal framework

### Option 3: Dual Licensing (Apache 2.0 + Commercial)
- Apache 2.0 for open source use
- Commercial license for proprietary enterprise features
- Maximum flexibility but increased complexity

## Decision Outcome

**Chosen Option**: **Apache 2.0 License (Option 2)**

### Rationale:

1. **Patent Protection**: Explicit patent grant protects users and encourages enterprise adoption
2. **Industry Standard**: Used by major AI frameworks (TensorFlow, Kubernetes, many Apache projects)
3. **Contributor Protection**: Strong legal framework protects contributors
4. **Enterprise Acceptance**: Widely accepted and understood by enterprise legal teams
5. **Steel Browser Compatibility**: Compatible with Steel Browser's licensing

### License Application:

- **Core Framework**: Apache 2.0 for all open source components
- **Premium Examples**: Proprietary license for commercial tier
- **Documentation**: Creative Commons Attribution 4.0 for comprehensive docs
- **Steel Browser Fork**: Maintain original Steel Browser license with Apache 2.0 additions

## Positive Consequences

- **Strong Legal Foundation**: Comprehensive patent and contribution protections
- **Enterprise Confidence**: Well-understood license reduces legal friction
- **Community Trust**: Recognized OSI-approved license
- **Innovation Protection**: Patent grant encourages derivative works and contributions
- **Compatibility**: Works well with existing dependencies and ecosystem

## Negative Consequences

- **Slightly More Complex**: More comprehensive terms than MIT
- **Patent Obligations**: Contributors must grant patent rights
- **Commercial Considerations**: Requires careful management of dual licensing model

### Mitigation Strategies

- **Clear Documentation**: Comprehensive licensing guide for contributors and users
- **Legal Review**: Regular legal review of licensing compliance
- **Contributor Education**: Clear contributor license agreement (CLA) process
- **Patent Policy**: Transparent patent policy for framework innovations

## Pros and Cons of the Options

### MIT License
**Pros:**
- Simplest possible terms
- Maximum permissiveness
- Familiar to most developers
- Minimal legal overhead
- Universal compatibility

**Cons:**
- No explicit patent grant
- Limited contributor protection
- May create patent uncertainty for enterprises
- Less comprehensive legal framework
- Potential IP complications

### Apache 2.0 License
**Pros:**
- Explicit patent grant protects users
- Strong contributor protection
- Enterprise-friendly legal framework
- Widely adopted by major projects
- Comprehensive license terms
- Compatible with most other licenses

**Cons:**
- More complex than MIT
- Patent grant requirements for contributors
- Slightly more restrictive than MIT
- Requires more legal documentation

### Dual Licensing
**Pros:**
- Maximum flexibility for different use cases
- Clear commercial path for enterprise features
- Can optimize license for each use case
- Potential revenue from commercial licenses

**Cons:**
- Significant legal complexity
- Confusion for users about which license applies
- High administrative overhead
- May limit community contributions
- Complex compliance requirements

## Implementation Requirements

### License Application Process

1. **File Headers**: Add Apache 2.0 header to all source files
   ```
   Copyright 2025 Agent Forge Contributors
   
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
   
       http://www.apache.org/licenses/LICENSE-2.0
   ```

2. **LICENSE File**: Include complete Apache 2.0 license text in repository root

3. **NOTICE File**: Create NOTICE file listing all contributors and attributions

4. **Third-Party Licenses**: Document all dependency licenses in THIRD_PARTY_LICENSES.md

### Contributor License Agreement (CLA)

Implement lightweight CLA process:
- **Individual CLA**: For individual contributors
- **Corporate CLA**: For company employees contributing
- **Automated Process**: GitHub bot for CLA signature tracking
- **Clear Terms**: Transparent explanation of contributor rights and obligations

### Patent Policy

Establish clear patent policy:
- **Defensive Use**: Patents used only for defensive purposes
- **Open Innovation**: Encourage patent-free innovation in AI automation
- **Clear Boundaries**: Define what constitutes framework vs. application IP
- **Community Benefits**: Ensure patent policy benefits entire community

## Legal Compliance Framework

### License Scanning
- **Automated Tools**: FOSSA, Licensee, or similar for dependency scanning
- **Regular Audits**: Quarterly license compliance reviews
- **Incompatible Licenses**: Process for handling GPL or other restrictive licenses
- **Documentation**: Maintain comprehensive license inventory

### Enterprise Support
- **Legal FAQ**: Common legal questions for enterprise customers
- **License Compatibility**: Guidance on using Agent Forge with other software
- **Compliance Support**: Resources for enterprise legal teams
- **Patent Clearance**: Process for enterprise patent clearance requests

## Documentation Requirements

### User-Facing Documentation
- **LICENSE.md**: Clear explanation of Apache 2.0 terms for users
- **CONTRIBUTING.md**: Licensing requirements for contributors
- **FAQ**: Common licensing questions and answers
- **Enterprise Guide**: Licensing guidance for enterprise adoption

### Internal Documentation
- **Legal Checklist**: Comprehensive compliance checklist
- **Review Process**: Regular legal review procedures
- **Policy Updates**: Process for updating licensing policies
- **Training Materials**: Team education on licensing requirements

## Success Metrics

- **Enterprise Adoption**: No licensing-related barriers to enterprise customers
- **Contributor Confidence**: Clear contributor agreement and protection
- **Legal Clarity**: Zero licensing-related support tickets or confusion
- **Compliance**: 100% license compliance across all dependencies
- **Community Trust**: Positive community feedback on licensing approach

## Links

- [Apache 2.0 License Text](https://www.apache.org/licenses/LICENSE-2.0)
- [Apache License FAQ](https://www.apache.org/foundation/license-faq.html)
- [GitHub CLA Best Practices](https://docs.github.com/en/github/site-policy/github-terms-for-additional-products-and-features#contributor-license-agreement)
- [Open Source License Compatibility](https://www.gnu.org/licenses/license-compatibility.html)
- [Enterprise Open Source Legal Guide](https://www.linuxfoundation.org/resources/open-source-guides/enterprise-open-source-practical-introduction/)
- [Steel Browser License](https://github.com/steel-dev/steel-browser/blob/main/LICENSE)
- [FOSSA License Scanning](https://fossa.com/)
- [OSI Approved Licenses](https://opensource.org/licenses/)
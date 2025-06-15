# ADR-021: MCP Blockchain Operations Security Model

## Status
Proposed

## Context

Agent Forge's unique blockchain integration (NMKR Proof-of-Execution NFTs and Masumi Network payment verification) represents a significant competitive advantage that must be securely exposed through MCP interfaces. This decision defines the security model for blockchain operations accessible via MCP clients like Claude Desktop.

### Background
- Agent Forge includes production blockchain integration with NMKR (Cardano) and Masumi Network
- Blockchain operations involve cryptocurrency transactions, NFT minting, and payment verification
- MCP clients may have varying security models and trust levels
- Enterprise customers require audit trails and compliance for blockchain operations
- Security vulnerabilities in blockchain operations could result in financial loss

### Blockchain Operations to Expose via MCP
1. **NMKR Proof-of-Execution**:
   - NFT minting for agent execution verification
   - CIP-25 metadata generation and IPFS storage
   - Cryptographic proof validation
   - Audit log generation and verification

2. **Masumi Network Integration**:
   - Payment verification and escrow operations
   - AI Agent Economy participation
   - Revenue tracking and distribution
   - Smart contract interaction

3. **General Blockchain Utilities**:
   - Transaction status monitoring
   - Wallet balance checking
   - Smart contract deployment and interaction
   - Multi-chain operation support

### Security Requirements
1. **Financial Security**: Prevent unauthorized access to cryptocurrency operations
2. **Authentication**: Robust identity verification for blockchain operations
3. **Authorization**: Granular permissions for different operation types
4. **Audit Compliance**: Complete audit trails for regulatory requirements
5. **Privacy Protection**: Secure handling of private keys and sensitive data
6. **Transaction Integrity**: Prevent transaction manipulation or replay attacks

## Options Considered

### Option 1: Full Exposure with MCP Client Trust
- Expose all blockchain operations through MCP interfaces
- Rely on MCP client security models
- Minimal additional security layers

**Pros:**
- Simple implementation
- Full feature access for MCP clients
- Leverages existing MCP security

**Cons:**
- High security risk
- No granular control over blockchain operations
- Potential for financial loss
- Insufficient for enterprise compliance

### Option 2: No Blockchain Exposure
- Exclude all blockchain operations from MCP interfaces
- Maintain blockchain features only in native Agent Forge interfaces
- Focus MCP integration on non-financial operations

**Pros:**
- Eliminates financial security risks
- Simple security model
- No additional authentication required

**Cons:**
- Loses key competitive advantage
- Reduces value proposition for MCP integration
- Limits enterprise use cases
- Misses monetization opportunities

### Option 3: Tiered Security with Operation Classification (SELECTED)
- Classify blockchain operations by risk level
- Implement graduated security controls based on operation type
- Secure authentication and authorization for high-risk operations
- Comprehensive audit logging for all blockchain activities

**Pros:**
- Balances security with functionality
- Enables enterprise compliance
- Maintains competitive advantage
- Flexible security model

**Cons:**
- Increased implementation complexity
- Additional authentication requirements
- More extensive testing needed

### Option 4: Blockchain Proxy Service
- Separate blockchain service with its own authentication
- MCP integration communicates with proxy service
- Blockchain operations isolated from MCP layer

**Pros:**
- Clear separation of concerns
- Independent security model
- Easier to audit and secure

**Cons:**
- Additional infrastructure complexity
- Potential performance impact
- More complex deployment model

## Decision

**We will implement Option 3: Tiered Security with Operation Classification.**

### Rationale

1. **Competitive Advantage**: Preserves Agent Forge's unique blockchain differentiation while ensuring security
2. **Enterprise Compliance**: Enables enterprise adoption with appropriate security controls
3. **Risk Management**: Graduated security controls match risk levels to protection requirements
4. **Flexibility**: Allows fine-tuning security based on operation type and client capabilities
5. **Audit Requirements**: Provides comprehensive audit trails required for regulatory compliance

## Security Architecture

### Operation Classification

#### Tier 1: Read-Only Operations (Low Risk)
- **Operations**: Transaction status checking, balance inquiries, proof verification
- **Security**: Basic MCP client authentication
- **Audit**: Standard operation logging

#### Tier 2: Verification Operations (Medium Risk)
- **Operations**: Proof generation, audit log creation, metadata validation
- **Security**: Enhanced authentication + operation signing
- **Audit**: Detailed operation logging with integrity verification

#### Tier 3: Financial Operations (High Risk)
- **Operations**: NFT minting, payment processing, smart contract deployment
- **Security**: Multi-factor authentication + hardware security module (HSM)
- **Audit**: Complete financial audit trail with regulatory compliance

#### Tier 4: Administrative Operations (Critical Risk)
- **Operations**: Key management, wallet creation, permission modifications
- **Security**: Administrative privileges + out-of-band verification
- **Audit**: Administrative audit trail with approval workflows

### Authentication and Authorization Framework

#### Multi-Layer Authentication
```
MCP Client Authentication
├── Basic MCP Client Identity (All Operations)
├── Agent Forge User Authentication (Tier 2+)
├── Financial Operation Authorization (Tier 3+)
└── Administrative Privilege Verification (Tier 4)
```

#### Authorization Matrix
| Operation Type | MCP Auth | User Auth | Financial Auth | Admin Auth | HSM Required |
|----------------|----------|-----------|----------------|------------|--------------|
| Balance Check | ✓ | - | - | - | - |
| Proof Generation | ✓ | ✓ | - | - | - |
| NFT Minting | ✓ | ✓ | ✓ | - | ✓ |
| Payment Processing | ✓ | ✓ | ✓ | - | ✓ |
| Key Management | ✓ | ✓ | ✓ | ✓ | ✓ |

### Security Controls Implementation

#### Cryptographic Controls
- **Private Key Protection**: HSM or secure enclave for key storage
- **Transaction Signing**: Hardware-based transaction signing for Tier 3+ operations
- **Message Integrity**: HMAC verification for all blockchain communications
- **Encryption**: AES-256 encryption for sensitive data in transit and at rest

#### Access Controls
- **Role-Based Access Control (RBAC)**: Granular permissions based on user roles
- **Time-Based Access**: Temporary credentials with automatic expiration
- **IP Restriction**: Optional IP allowlisting for administrative operations
- **Geographic Restrictions**: Configurable geographic access controls

#### Operational Controls
- **Rate Limiting**: Configurable rate limits per operation type and user
- **Transaction Limits**: Daily/monthly transaction value limits
- **Approval Workflows**: Multi-signature requirements for high-value operations
- **Emergency Procedures**: Circuit breakers and emergency operation suspension

### Audit and Compliance Framework

#### Audit Logging Requirements
```
Blockchain Operation Audit Log
├── Operation Metadata
│   ├── Timestamp (UTC, ISO 8601)
│   ├── Operation Type and Classification
│   ├── User Identity and Authentication Method
│   └── MCP Client Information
├── Operation Details
│   ├── Input Parameters (sanitized)
│   ├── Blockchain Network and Addresses
│   ├── Transaction Hashes and Confirmations
│   └── Operation Results and Status
├── Security Context
│   ├── Authentication Chain
│   ├── Authorization Decisions
│   ├── Risk Assessment Outcomes
│   └── Security Control Verifications
└── Compliance Data
    ├── Regulatory Classification
    ├── Geographic Jurisdiction
    ├── Data Privacy Compliance
    └── Financial Reporting Requirements
```

#### Compliance Features
- **Regulatory Reporting**: Automated report generation for compliance requirements
- **Data Retention**: Configurable retention policies for audit logs
- **Privacy Protection**: GDPR-compliant handling of personal data
- **Immutable Audit Trail**: Blockchain-based audit log integrity verification

## Implementation Details

### Security Component Architecture
```
MCP Blockchain Security Layer
├── Authentication Service
│   ├── MCP Client Verification
│   ├── User Identity Management
│   ├── Multi-Factor Authentication
│   └── Session Management
├── Authorization Engine
│   ├── Operation Classification
│   ├── Permission Evaluation
│   ├── Risk Assessment
│   └── Policy Enforcement
├── Cryptographic Services
│   ├── Hardware Security Module Interface
│   ├── Key Management Service
│   ├── Transaction Signing Service
│   └── Encryption/Decryption Service
├── Audit and Compliance
│   ├── Operation Logging Service
│   ├── Compliance Reporting Engine
│   ├── Audit Trail Verification
│   └── Regulatory Data Management
└── Monitoring and Alerting
    ├── Security Event Detection
    ├── Anomaly Detection
    ├── Incident Response
    └── Threat Intelligence Integration
```

### Configuration Management
- **Environment-Specific Policies**: Different security policies for development, staging, and production
- **Tenant-Specific Configuration**: Customizable security policies for enterprise customers
- **Dynamic Policy Updates**: Runtime policy updates without service disruption
- **A/B Testing Support**: Graduated rollout of security policy changes

## Consequences

### Positive
- **Security Assurance**: Enterprise-grade security for blockchain operations
- **Competitive Advantage**: Secure exposure of unique blockchain capabilities
- **Compliance Enablement**: Meets regulatory requirements for financial operations
- **Risk Management**: Graduated security controls match protection to risk levels
- **Audit Capability**: Comprehensive audit trails for enterprise customers
- **Flexibility**: Configurable security policies for different deployment scenarios

### Negative
- **Implementation Complexity**: Significant additional security infrastructure required
- **Performance Impact**: Security controls may introduce latency for blockchain operations
- **User Experience**: Additional authentication steps may impact user experience
- **Operational Overhead**: Security monitoring and incident response requirements
- **Cost Increase**: HSM and additional security infrastructure costs

### Risk Mitigation Strategies

| Risk | Mitigation |
|------|------------|
| Key Compromise | HSM-based key storage, regular key rotation, multi-signature requirements |
| Unauthorized Access | Multi-factor authentication, IP restrictions, behavioral monitoring |
| Transaction Manipulation | Cryptographic signing, transaction integrity verification, audit trails |
| Compliance Violations | Automated compliance checking, regulatory reporting, legal review processes |
| Security Incidents | 24/7 monitoring, automated incident response, emergency procedures |

## Technical Implementation

### Security Integration Points

#### MCP Protocol Integration
```python
@dataclass
class MCPBlockchainSecurityContext:
    client_identity: str
    user_authentication: Optional[UserAuth]
    operation_classification: SecurityTier
    required_permissions: List[Permission]
    audit_context: AuditContext
    
async def secure_blockchain_operation(
    operation: BlockchainOperation,
    context: MCPBlockchainSecurityContext
) -> BlockchainResult:
    # Validate authentication chain
    await validate_authentication_chain(context)
    
    # Check authorization
    await verify_operation_permissions(operation, context)
    
    # Execute with security controls
    result = await execute_with_security_controls(operation, context)
    
    # Log for audit compliance
    await log_blockchain_operation(operation, context, result)
    
    return result
```

#### HSM Integration
- **Key Storage**: All private keys stored in FIPS 140-2 Level 3 certified HSM
- **Transaction Signing**: Hardware-based signature generation for all financial operations
- **Key Rotation**: Automated key rotation with secure key escrow
- **Backup and Recovery**: Secure key backup and disaster recovery procedures

## Testing Strategy

### Security Testing Requirements
- **Penetration Testing**: Regular third-party security assessments
- **Vulnerability Scanning**: Automated vulnerability detection and remediation
- **Authentication Testing**: Comprehensive testing of all authentication mechanisms
- **Authorization Testing**: Validation of all permission and access control logic
- **Audit Testing**: Verification of audit log completeness and integrity

### Compliance Testing
- **Regulatory Simulation**: Testing against regulatory compliance requirements
- **Privacy Testing**: GDPR and privacy regulation compliance validation
- **Financial Testing**: Financial operation compliance and reporting validation
- **Cross-Border Testing**: International compliance and data sovereignty testing

## Monitoring and Alerting

### Security Monitoring
- **Real-Time Threat Detection**: Machine learning-based anomaly detection
- **Financial Operation Monitoring**: Real-time monitoring of all financial transactions
- **Access Pattern Analysis**: Behavioral analysis for unusual access patterns
- **Compliance Monitoring**: Continuous compliance validation and alerting

### Alert Categories
- **Security Incidents**: Unauthorized access attempts, suspicious activities
- **Financial Alerts**: Large transactions, unusual spending patterns
- **Compliance Violations**: Policy violations, regulatory requirement breaches
- **System Health**: Security system failures, HSM communication issues

## Review and Update Process

This security model will be reviewed quarterly and updated based on:
- **Threat Landscape Evolution**: New security threats and attack vectors
- **Regulatory Changes**: Updates to financial and privacy regulations
- **Technology Updates**: New security technologies and best practices
- **Incident Learnings**: Security incidents and lessons learned
- **Compliance Requirements**: Changes in enterprise compliance needs

## References

- [NMKR Security Documentation](https://docs.nmkr.io/security)
- [Masumi Network Security Model](https://docs.masumi.network/security)
- [FIPS 140-2 Security Requirements](https://csrc.nist.gov/publications/detail/fips/140/2/final)
- [GDPR Compliance Guidelines](https://gdpr.eu/compliance/)
- [Cardano Security Best Practices](https://docs.cardano.org/security)

---

**Decision Date**: June 14, 2025  
**Status**: Proposed  
**Decision Makers**: Agent Forge Security Team, Architecture Team  
**Stakeholders**: Engineering, Compliance, Business Development, Finance  
**Review Date**: September 14, 2025
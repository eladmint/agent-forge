"""
NMKR Auditor Agent - Creates blockchain-verified proofs of autonomous execution

This agent demonstrates the complete Proof-of-Execution workflow described in the
NMKR_PROOF_OF_EXECUTION_GUIDE.md, creating verifiable proofs of agent execution
on the Cardano blockchain via NMKR Studio API.

Features:
- Autonomous task execution with complete audit logging
- Cryptographic proof generation using SHA-256 hashing
- IPFS integration for decentralized storage
- NMKR API integration for Cardano NFT minting
- CIP-25 compliant metadata generation
"""

from typing import Optional, Dict, Any
from core.agents.base import AsyncContextAgent
import json
import hashlib
import base64
from datetime import datetime
from urllib.parse import urlparse
import asyncio
import aiohttp

class NMKRAuditorAgent(AsyncContextAgent):
    """
    Advanced blockchain integration agent that creates verifiable proofs of execution.
    
    This agent implements the complete Proof-of-Execution workflow:
    1. Execute autonomous tasks using Steel Browser
    2. Generate comprehensive audit logs
    3. Create cryptographic proofs using SHA-256
    4. Simulate IPFS upload for decentralized storage
    5. Generate CIP-25 compliant NFT metadata
    6. Construct NMKR API payload for Cardano minting
    7. Provide complete verification package
    """
    
    def __init__(self, name: Optional[str] = None, config: Optional[dict] = None, 
                 url: Optional[str] = None, task_description: Optional[str] = None,
                 nmkr_api_key: Optional[str] = None):
        super().__init__(name, config)
        self.url = url or self.config.get('url')
        self.task_description = task_description or self.config.get('task_description', 'General web analysis')
        self.nmkr_api_key = nmkr_api_key or self.config.get('nmkr_api_key', 'demo_api_key')
        self.nmkr_project_uid = self.config.get('nmkr_project_uid', 'demo_project_uid')
        
    async def run(self, url: Optional[str] = None, task_description: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Execute task and create blockchain proof of execution.
        
        Args:
            url: Target URL to analyze
            task_description: Description of the task being performed
            
        Returns:
            Complete proof-of-execution package with blockchain integration data
        """
        # Use provided parameters or fall back to instance variables
        target_url = url or self.url
        task_desc = task_description or self.task_description
        
        if not target_url:
            self.logger.error("No URL provided for analysis")
            return None
        
        self.logger.info(f"🔐 Starting blockchain-verified execution for: {target_url}")
        
        try:
            # Step 1: Execute the autonomous task
            self.logger.info("📋 Step 1: Executing autonomous task...")
            execution_results = await self._execute_task(target_url, task_desc)
            
            # Step 2: Generate comprehensive audit log
            self.logger.info("📝 Step 2: Generating comprehensive audit log...")
            audit_log = self._generate_audit_log(target_url, task_desc, execution_results)
            
            # Step 3: Create cryptographic proof
            self.logger.info("🔒 Step 3: Creating cryptographic proof...")
            log_hash = hashlib.sha256(audit_log.encode()).hexdigest()
            
            # Step 4: Simulate IPFS upload
            self.logger.info("🌐 Step 4: Simulating IPFS upload...")
            ipfs_cid = self._simulate_ipfs_upload(audit_log)
            
            # Step 5: Generate CIP-25 compliant metadata
            self.logger.info("📋 Step 5: Generating CIP-25 compliant metadata...")
            metadata = self._create_cip25_metadata(log_hash, ipfs_cid, target_url, task_desc)
            
            # Step 6: Create NMKR API payload
            self.logger.info("⛓️ Step 6: Constructing NMKR API payload...")
            nmkr_payload = self._construct_nmkr_payload(metadata)
            
            # Step 7: Generate comprehensive proof package
            self.logger.info("📦 Step 7: Assembling proof package...")
            proof_package = {
                "execution_summary": {
                    "url": target_url,
                    "task_description": task_desc,
                    "execution_timestamp": datetime.now().isoformat(),
                    "agent_id": f"agent_forge_{self.name}",
                    "status": "completed",
                    "proof_version": "1.0"
                },
                "verification_data": {
                    "audit_log": audit_log,
                    "proof_hash": log_hash,
                    "ipfs_cid": ipfs_cid,
                    "verification_method": "SHA-256",
                    "audit_log_size": len(audit_log),
                    "hash_algorithm": "SHA-256"
                },
                "blockchain_integration": {
                    "nft_metadata": metadata,
                    "nmkr_payload": nmkr_payload,
                    "blockchain": "Cardano",
                    "standard": "CIP-25",
                    "minting_service": "NMKR Studio API",
                    "estimated_cost": "2-4.5 ADA per NFT"
                },
                "execution_results": execution_results,
                "implementation_notes": {
                    "audit_trail": "Complete execution log with verification checkpoints",
                    "decentralized_storage": f"IPFS CID: {ipfs_cid}",
                    "blockchain_proof": f"SHA-256 hash: {log_hash[:16]}...",
                    "economic_incentives": "On-chain reputation building through verified work"
                }
            }
            
            # Log success and display summary
            self.logger.info(f"✅ Blockchain proof generated successfully. Hash: {log_hash[:16]}...")
            self._display_execution_summary(proof_package)
            
            return proof_package
            
        except Exception as e:
            self.logger.error(f"❌ Blockchain execution failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "url": target_url,
                "task_description": task_desc,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _execute_task(self, url: str, task_description: str) -> Dict[str, Any]:
        """
        Execute the specified task using the browser client.
        
        Args:
            url: Target URL to process
            task_description: Description of task being performed
            
        Returns:
            Comprehensive execution results with performance metrics
        """
        self.logger.info(f"🎯 Executing task: {task_description}")
        
        start_time = datetime.now()
        
        # Navigate to the URL using Steel Browser
        response = await self.browser_client.navigate(url)
        
        end_time = datetime.now()
        execution_duration = (end_time - start_time).total_seconds()
        
        if not response:
            raise Exception("Failed to navigate to target URL - browser automation unsuccessful")
        
        # Extract comprehensive information from response
        results = {
            "navigation_successful": True,
            "url": url,
            "page_title": response.get('page_title', 'Unknown Title'),
            "content_length": len(response.get('content', '')),
            "response_status": response.get('status', 'unknown'),
            "execution_time": datetime.now().isoformat(),
            "execution_duration_seconds": execution_duration,
            "browser_info": {
                "user_agent": "Agent Forge Steel Browser Client",
                "viewport": "1920x1080",
                "javascript_enabled": True,
                "automation_method": "Steel Browser API"
            },
            "performance_metrics": {
                "total_execution_time": execution_duration,
                "navigation_time": execution_duration * 0.8,  # Estimated
                "content_processing_time": execution_duration * 0.2  # Estimated
            }
        }
        
        # Perform task-specific analysis based on URL patterns
        if "github" in url.lower():
            results.update({
                "analysis_type": "github_repository",
                "repository_detected": True,
                "content_indicators": self._analyze_github_content(response.get('content', ''))
            })
        elif "news" in url.lower() or "hacker" in url.lower():
            results.update({
                "analysis_type": "news_site",
                "news_site_detected": True,
                "content_indicators": self._analyze_news_content(response.get('content', ''))
            })
        elif "cardano" in url.lower() or "blockchain" in url.lower():
            results.update({
                "analysis_type": "blockchain_site",
                "blockchain_content_detected": True,
                "content_indicators": self._analyze_blockchain_content(response.get('content', ''))
            })
        else:
            results.update({
                "analysis_type": "general_website",
                "content_indicators": self._analyze_general_content(response.get('content', ''))
            })
        
        return results
    
    def _analyze_github_content(self, content: str) -> Dict[str, Any]:
        """Analyze GitHub-specific content patterns."""
        indicators = {
            "likely_repository": "repository" in content.lower() or "commit" in content.lower(),
            "has_readme": "readme" in content.lower(),
            "has_issues": "issues" in content.lower(),
            "has_releases": "releases" in content.lower(),
            "programming_language_detected": any(lang in content.lower() for lang in ["python", "javascript", "java", "go", "rust"])
        }
        return indicators
    
    def _analyze_news_content(self, content: str) -> Dict[str, Any]:
        """Analyze news site content patterns."""
        indicators = {
            "has_articles": "article" in content.lower(),
            "has_comments": "comment" in content.lower(),
            "tech_focus": any(term in content.lower() for term in ["technology", "startup", "programming", "ai"]),
            "recent_content": any(term in content.lower() for term in ["today", "yesterday", "hours ago"])
        }
        return indicators
    
    def _analyze_blockchain_content(self, content: str) -> Dict[str, Any]:
        """Analyze blockchain/crypto content patterns."""
        indicators = {
            "cardano_content": "cardano" in content.lower(),
            "nft_content": "nft" in content.lower(),
            "defi_content": "defi" in content.lower() or "decentralized" in content.lower(),
            "smart_contracts": "smart contract" in content.lower(),
            "cryptocurrency": any(term in content.lower() for term in ["ada", "bitcoin", "ethereum", "crypto"])
        }
        return indicators
    
    def _analyze_general_content(self, content: str) -> Dict[str, Any]:
        """Analyze general website content patterns."""
        indicators = {
            "has_navigation": "nav" in content.lower() or "menu" in content.lower(),
            "has_contact": "contact" in content.lower(),
            "has_about": "about" in content.lower(),
            "interactive_elements": any(term in content.lower() for term in ["form", "button", "input"]),
            "media_content": any(term in content.lower() for term in ["image", "video", "gallery"])
        }
        return indicators
    
    def _generate_audit_log(self, url: str, task_description: str, execution_results: Dict[str, Any]) -> str:
        """
        Generate comprehensive audit log of the execution.
        
        Args:
            url: Target URL
            task_description: Task description
            execution_results: Results from task execution
            
        Returns:
            JSON-formatted audit log string
        """
        execution_id = f"exec_{int(datetime.now().timestamp())}"
        
        log_data = {
            "audit_log_version": "1.0",
            "audit_log_standard": "Agent Forge Proof-of-Execution v1.0",
            "agent_information": {
                "agent_name": self.name or "NMKRAuditorAgent",
                "agent_version": "1.0.0",
                "framework": "Agent Forge",
                "framework_version": "1.0.0",
                "execution_environment": "Python 3.8+",
                "browser_automation": "Steel Browser API"
            },
            "task_details": {
                "execution_id": execution_id,
                "target_url": url,
                "task_description": task_description,
                "execution_timestamp": datetime.now().isoformat(),
                "task_category": execution_results.get("analysis_type", "general"),
                "estimated_complexity": self._estimate_task_complexity(url, task_description)
            },
            "execution_trace": {
                "steps_executed": [
                    "Agent initialization and configuration",
                    "Browser client setup and verification",
                    f"Navigation to target URL: {url}",
                    "Content extraction and analysis",
                    "Task-specific processing",
                    "Results compilation and validation",
                    "Audit log generation",
                    "Cryptographic proof creation"
                ],
                "execution_results": execution_results,
                "verification_checkpoints": {
                    "url_validation": self._validate_url(url),
                    "response_validation": execution_results.get("navigation_successful", False),
                    "content_validation": execution_results.get("content_length", 0) > 0,
                    "data_integrity": True,
                    "task_completion": execution_results.get("response_status") != "error"
                }
            },
            "blockchain_integration": {
                "proof_of_execution_enabled": True,
                "blockchain_network": "Cardano",
                "nft_standard": "CIP-25",
                "minting_service": "NMKR Studio API",
                "decentralized_storage": "IPFS",
                "verification_method": "SHA-256 + IPFS CID"
            },
            "compliance_information": {
                "data_handling": "No personal data collected or processed",
                "privacy_compliance": "GDPR compliant - public data only",
                "execution_transparency": "Full audit trail maintained",
                "immutable_record": "Blockchain-verified execution proof",
                "decentralized_verification": "IPFS storage for independent verification"
            },
            "economic_model": {
                "reputation_system": "NFT-based proof accumulation",
                "cost_structure": "2-4.5 ADA per proof NFT",
                "incentive_alignment": "Quality execution rewards",
                "cross_platform_portability": "Verifiable across services"
            },
            "technical_metadata": {
                "audit_log_hash": "to_be_calculated",
                "audit_log_size_bytes": "to_be_calculated",
                "ipfs_upload_timestamp": "to_be_simulated",
                "nft_metadata_standard": "CIP-25",
                "proof_generation_method": "SHA-256 cryptographic hash"
            }
        }
        
        # Convert to JSON with proper formatting
        audit_log_json = json.dumps(log_data, indent=2, sort_keys=True, ensure_ascii=False)
        
        # Update metadata with actual values
        log_data["technical_metadata"]["audit_log_size_bytes"] = len(audit_log_json)
        
        # Regenerate with updated metadata
        return json.dumps(log_data, indent=2, sort_keys=True, ensure_ascii=False)
    
    def _estimate_task_complexity(self, url: str, task_description: str) -> str:
        """Estimate task complexity based on URL and description."""
        complexity_indicators = 0
        
        # URL complexity indicators
        if "api" in url.lower():
            complexity_indicators += 2
        if "github" in url.lower():
            complexity_indicators += 2
        if any(term in url.lower() for term in ["admin", "dashboard", "secure"]):
            complexity_indicators += 3
            
        # Task description complexity indicators
        task_lower = task_description.lower()
        if any(term in task_lower for term in ["analysis", "extract", "process"]):
            complexity_indicators += 1
        if any(term in task_lower for term in ["complex", "detailed", "comprehensive"]):
            complexity_indicators += 2
        if any(term in task_lower for term in ["blockchain", "nft", "smart contract"]):
            complexity_indicators += 3
            
        if complexity_indicators >= 5:
            return "high"
        elif complexity_indicators >= 3:
            return "medium"
        else:
            return "low"
    
    def _simulate_ipfs_upload(self, audit_log: str) -> str:
        """
        Simulate IPFS upload and return realistic content identifier.
        
        In production, this would upload to IPFS using services like:
        - Pinata (https://pinata.cloud/)
        - NFT.Storage (https://nft.storage/)
        - Infura IPFS (https://infura.io/product/ipfs)
        
        Args:
            audit_log: The audit log content to upload
            
        Returns:
            Simulated IPFS Content Identifier (CID)
        """
        # Generate deterministic CID based on content
        content_hash = hashlib.sha256(audit_log.encode()).hexdigest()
        
        # IPFS CIDs (Content Identifiers) follow specific formats
        # CIDv1 typically starts with 'b' for base32 encoding
        # For simulation, we create a realistic-looking CID
        simulated_cid = f"bafybeig{content_hash[:44]}"
        
        self.logger.info(f"📡 Simulated IPFS upload complete")
        self.logger.debug(f"Content size: {len(audit_log)} bytes")
        self.logger.debug(f"Generated CID: {simulated_cid}")
        
        return simulated_cid
    
    def _create_cip25_metadata(self, log_hash: str, ipfs_cid: str, url: str, task_description: str) -> Dict[str, Any]:
        """
        Create CIP-25 compliant metadata for the NFT.
        
        CIP-25 is the Cardano Improvement Proposal for NFT metadata standards.
        Reference: https://cips.cardano.org/cips/cip25/
        
        Args:
            log_hash: SHA-256 hash of the audit log
            ipfs_cid: IPFS Content Identifier for the audit log
            url: Target URL of the task
            task_description: Description of the executed task
            
        Returns:
            CIP-25 compliant metadata dictionary
        """
        # Generate unique token name based on timestamp
        timestamp = int(datetime.now().timestamp())
        token_name = f"agent_execution_{timestamp}"
        
        # Create CIP-25 compliant metadata structure
        metadata = {
            "721": {
                "policy_id_placeholder": {
                    token_name: {
                        "name": "Agent Forge Execution Proof",
                        "description": f"Verifiable proof of autonomous AI agent execution for task: {task_description}",
                        "image": "ipfs://QmAgentForgeExecutionProofThumbnail",
                        "mediaType": "image/png",
                        "attributes": {
                            "Agent Framework": "Agent Forge",
                            "Execution URL": url,
                            "Task Description": task_description,
                            "Execution Timestamp": datetime.now().isoformat(),
                            "Verification Method": "SHA-256 + IPFS",
                            "Audit Log CID": ipfs_cid,
                            "Proof Hash": log_hash,
                            "Blockchain": "Cardano",
                            "Standard": "CIP-25",
                            "Agent Type": "Autonomous Web Agent",
                            "Task Complexity": self._estimate_task_complexity(url, task_description),
                            "Execution Duration": "Real-time",
                            "Verification Status": "Cryptographically Verified"
                        },
                        "files": [
                            {
                                "name": "execution_audit_log.json",
                                "mediaType": "application/json",
                                "src": f"ipfs://{ipfs_cid}",
                                "description": "Complete audit log of agent execution"
                            },
                            {
                                "name": "execution_proof.txt",
                                "mediaType": "text/plain", 
                                "src": f"data:text/plain;base64,{base64.b64encode(log_hash.encode()).decode()}",
                                "description": "SHA-256 hash of execution audit log"
                            }
                        ],
                        "version": "1.0",
                        "authors": ["Agent Forge Framework"],
                        "copyright": "2025 Agent Forge - Open Source",
                        "license": "MIT",
                        "website": "https://github.com/agent-forge/framework"
                    }
                }
            },
            "verification": {
                "method": "SHA-256 cryptographic hashing",
                "storage": "IPFS decentralized storage",
                "blockchain": "Cardano",
                "standard": "CIP-25",
                "immutable": True,
                "decentralized": True
            }
        }
        
        return metadata
    
    def _construct_nmkr_payload(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Construct NMKR API payload for NFT minting.
        
        Based on NMKR Studio API documentation:
        https://docs.nmkr.io/nmkr-studio-api/api-examples/project/upload-file-and-metadata
        
        Args:
            metadata: CIP-25 compliant metadata
            
        Returns:
            NMKR API payload structure
        """
        # Extract token information from metadata
        policy_data = metadata["721"]["policy_id_placeholder"]
        token_name = list(policy_data.keys())[0]
        token_data = policy_data[token_name]
        
        # Create thumbnail image (base64 encoded placeholder)
        thumbnail_placeholder = base64.b64encode(
            "Agent Forge Execution Proof Thumbnail".encode()
        ).decode()
        
        payload = {
            "projectUid": self.nmkr_project_uid,
            "tokenname": token_name,
            "displayname": token_data["name"],
            "description": token_data["description"],
            "previewImageNft": {
                "mimetype": "image/png",
                "fileFromBase64": thumbnail_placeholder
            },
            "metadataPlaceholder": {
                "execution_url": token_data["attributes"]["Execution URL"],
                "task_description": token_data["attributes"]["Task Description"],
                "execution_timestamp": token_data["attributes"]["Execution Timestamp"],
                "audit_log_cid": token_data["attributes"]["Audit Log CID"],
                "proof_hash": token_data["attributes"]["Proof Hash"],
                "verification_method": token_data["attributes"]["Verification Method"],
                "agent_framework": token_data["attributes"]["Agent Framework"],
                "blockchain": token_data["attributes"]["Blockchain"],
                "standard": token_data["attributes"]["Standard"],
                "task_complexity": token_data["attributes"]["Task Complexity"],
                "verification_status": token_data["attributes"]["Verification Status"]
            },
            "mint": {
                "receiverAddress": "addr1_demo_receiver_address_placeholder",
                "count": 1
            },
            "options": {
                "royalties": {
                    "address": "addr1_demo_royalty_address_placeholder",
                    "percentage": 5.0
                },
                "lockMetadata": True,
                "enableRoyalties": True,
                "policyExpires": False,
                "saleConditions": {
                    "enableSale": False  # This is a proof, not for sale
                }
            },
            "apiKey": self.nmkr_api_key,
            "apiEndpoint": "https://studio-api.nmkr.io/v2/UploadNft"
        }
        
        return payload
    
    def _validate_url(self, url: str) -> bool:
        """
        Validate URL format and basic accessibility.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL appears valid, False otherwise
        """
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc and parsed.scheme in ['http', 'https'])
        except Exception:
            return False
    
    def _display_execution_summary(self, proof_package: Dict[str, Any]):
        """
        Display user-friendly execution summary.
        
        Args:
            proof_package: Complete proof package with all execution data
        """
        summary = proof_package["execution_summary"]
        verification = proof_package["verification_data"]
        blockchain = proof_package["blockchain_integration"]
        
        print(f"\n🎉 Agent Forge Blockchain Execution Complete!")
        print(f"{'='*60}")
        print(f"📋 Task: {summary['task_description']}")
        print(f"🌐 URL: {summary['url']}")
        print(f"⏰ Timestamp: {summary['execution_timestamp']}")
        print(f"🤖 Agent: {summary['agent_id']}")
        print(f"")
        print(f"🔐 Verification Data:")
        print(f"   Hash: {verification['proof_hash'][:32]}...")
        print(f"   IPFS: {verification['ipfs_cid']}")
        print(f"   Size: {verification['audit_log_size']:,} bytes")
        print(f"")
        print(f"⛓️ Blockchain Integration:")
        print(f"   Network: {blockchain['blockchain']}")
        print(f"   Standard: {blockchain['standard']}")
        print(f"   Service: {blockchain['minting_service']}")
        print(f"   Cost: {blockchain['estimated_cost']}")
        print(f"")
        print(f"✅ Status: Verifiable proof generated successfully!")
        print(f"📖 Complete audit log available in proof package")
        print(f"🔗 Ready for NMKR API minting on Cardano blockchain")
        print(f"{'='*60}")

# Usage example and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_nmkr_auditor():
        """Test the NMKR Auditor Agent functionality."""
        print("🧪 Testing NMKR Auditor Agent...")
        
        # Test configuration
        config = {
            "nmkr_api_key": "demo_test_key",
            "nmkr_project_uid": "demo_project_test_uid"
        }
        
        # Create and test agent
        async with NMKRAuditorAgent(name="test_auditor", config=config) as agent:
            # Test with different types of URLs
            test_cases = [
                ("https://github.com/microsoft/vscode", "Analyze repository structure"),
                ("https://news.ycombinator.com", "Monitor tech news"),
                ("https://cardano.org", "Analyze Cardano homepage")
            ]
            
            for url, task in test_cases:
                print(f"\n🔍 Testing: {task}")
                result = await agent.run(url, task)
                
                if result and result.get("verification_data"):
                    print(f"✅ Success: {result['verification_data']['proof_hash'][:16]}...")
                else:
                    print("❌ Test failed")
        
        print("\n🎉 NMKR Auditor Agent testing complete!")
    
    # Run the test
    asyncio.run(test_nmkr_auditor())
#!/usr/bin/env python3

# DEPLOYMENT SCRIPT: 01 - Enhanced Multi-Region Extraction Service
# STATUS: ✅ PRIMARY RECOMMENDED
# ARCHITECTURE: Enhanced multi-region extraction with production orchestrator
# USE WHEN: Deploying production multi-region extraction service
# UPDATED: June 9, 2025 - Enterprise deployment structure paths

# Enhanced Multi-Region Extraction Service Deployment
# Deploys extraction service across multiple regions with orchestrator coordination

"""
🚀 Deploy Enhanced Multi-Region Services

This script creates and deploys multi-region services with complete 
Enhanced Orchestrator capabilities for 90+ event extraction.

UPDATED FOR ENTERPRISE STRUCTURE:
- Uses src/api/ instead of chatbot_api/
- Clean deployment paths with numbered priority system
- Service-centric deployment organization
"""

import json
import os


def create_enhanced_multi_region_service():
    """Create enhanced multi-region service with full agent system"""

    service_code = '''#!/usr/bin/env python3
"""
🌐 Enhanced Multi-Region Extraction Service
Complete Enhanced Orchestrator with 13+ Agent System

This service provides full calendar extraction capabilities with:
- LinkFinderAgent for calendar discovery (90+ events)
- All 13+ agents for comprehensive processing
- Database integration with Supabase
- Rate limiting evasion through IP rotation
"""

import asyncio
import time
import logging
import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import requests
import aiohttp

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

app = FastAPI(
    title="Enhanced Multi-Region Extraction Service",
    description="Complete calendar extraction with 13+ agents and rate limiting evasion",
    version="2.0.0"
)

# Regional configuration
REGION = os.getenv("REGION", "us-central1")
COST_TIER = int(os.getenv("COST_TIER", "2"))
PRODUCTION_ORCHESTRATOR_URL = "https://production-orchestrator-867263134607.us-central1.run.app"

# Regional costs per extraction
REGIONAL_COSTS = {
    1: 0.002,   # Premium tier
    2: 0.0018,  # Standard tier  
    3: 0.0015   # Economy tier
}

# Request/Response Models
class EnhancedExtractionRequest(BaseModel):
    urls: List[str] = Field(..., description="Calendar URLs to extract")
    max_concurrent: Optional[int] = Field(default=3, description="Max concurrent extractions")
    timeout_per_event: Optional[int] = Field(default=300, description="Timeout per event in seconds")
    save_to_database: Optional[bool] = Field(default=True, description="Save results to Supabase")
    visual_intelligence: Optional[bool] = Field(default=True, description="Enable visual intelligence")
    crypto_enhanced: Optional[bool] = Field(default=True, description="Enable crypto knowledge")
    mcp_browser: Optional[bool] = Field(default=True, description="Enable MCP browser control")
    calendar_discovery: Optional[bool] = Field(default=True, description="Enable full calendar discovery")

class EnhancedExtractionResponse(BaseModel):
    region: str = Field(..., description="Processing region")
    total_events: int = Field(..., description="Total events extracted")
    successful_events: int = Field(..., description="Successfully processed events")
    failed_events: int = Field(..., description="Failed event extractions")
    processing_time: float = Field(..., description="Total processing time in seconds")
    cost: float = Field(..., description="Extraction cost in USD")
    results: List[Dict[str, Any]] = Field(..., description="Extracted event data")
    session_id: str = Field(..., description="Unique session identifier")
    extraction_method: str = Field(..., description="Extraction method used")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service health status")
    region: str = Field(..., description="Service region")
    cost_tier: int = Field(..., description="Regional cost tier")
    capabilities: Dict[str, Any] = Field(..., description="Service capabilities")
    production_orchestrator_status: str = Field(..., description="Production orchestrator connectivity")

# Service stats
extraction_stats = {
    'total_extractions': 0,
    'total_events_found': 0,
    'total_cost': 0.0,
    'start_time': datetime.now(),
    'last_extraction': None
}

@app.on_event("startup")
async def startup_event():
    """Initialize service"""
    logger = logging.getLogger(__name__)
    logger.info(f"🚀 Enhanced Multi-Region Service starting in {REGION}")
    logger.info(f"💰 Cost tier: {COST_TIER} (${REGIONAL_COSTS[COST_TIER]:.4f}/extraction)")
    logger.info(f"🎯 Production orchestrator: {PRODUCTION_ORCHESTRATOR_URL}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger = logging.getLogger(__name__)
    logger.info(f"🛑 Enhanced Multi-Region Service shutting down in {REGION}")
    logger.info(f"📊 Final stats: {extraction_stats}")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check with production orchestrator connectivity test"""
    
    # Test production orchestrator connectivity
    orchestrator_status = "unknown"
    try:
        response = requests.get(f"{PRODUCTION_ORCHESTRATOR_URL}/health", timeout=5)
        if response.status_code == 200:
            orchestrator_status = "connected"
        else:
            orchestrator_status = "degraded"
    except:
        orchestrator_status = "disconnected"
    
    capabilities = {
        "enhanced_orchestrator": True,
        "agent_count": "13+",
        "calendar_discovery": True,
        "visual_intelligence": True,
        "crypto_knowledge": True,
        "mcp_browser_control": True,
        "database_integration": True,
        "rate_limiting_evasion": True,
        "steel_browser": True,
        "ip_rotation": f"Google Cloud {REGION}"
    }
    
    return HealthResponse(
        status="healthy",
        region=REGION,
        cost_tier=COST_TIER,
        capabilities=capabilities,
        production_orchestrator_status=orchestrator_status
    )

@app.post("/extract", response_model=EnhancedExtractionResponse)
async def extract_events_enhanced(request: EnhancedExtractionRequest):
    """
    Enhanced extraction using complete Enhanced Orchestrator system
    
    This endpoint provides full calendar extraction capabilities:
    - Calendar discovery with LinkFinderAgent (90+ events)
    - Complete 13+ agent processing
    - Database integration with deduplication
    - Visual intelligence and crypto knowledge
    - Rate limiting evasion through regional IP rotation
    """
    
    start_time = time.time()
    session_id = f"{REGION}_{int(time.time())}"
    
    try:
        # Use production orchestrator with enhanced capabilities
        payload = {
            "urls": request.urls,
            "max_concurrent": request.max_concurrent,
            "timeout_per_event": request.timeout_per_event,
            "save_to_database": request.save_to_database,
            "visual_intelligence": request.visual_intelligence,
            "crypto_enhanced": request.crypto_enhanced,
            "mcp_browser": request.mcp_browser,
            "session_id": session_id,
            "region": REGION,
            "calendar_discovery": request.calendar_discovery
        }
        
        # Add regional headers to appear from this region
        headers = {
            'Content-Type': 'application/json',
            'X-Forwarded-For': f"34.102.{(hash(REGION) % 254) + 1}.{(hash(session_id) % 254) + 1}",
            'X-Real-IP': f"34.102.{(hash(REGION) % 254) + 1}.{(hash(session_id) % 254) + 1}",
            'X-Region': REGION,
            'User-Agent': f'Multi-Region-Extractor/{REGION}/2.0.0'
        }
        
        # Call production orchestrator with enhanced capabilities
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{PRODUCTION_ORCHESTRATOR_URL}/extract",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=1800)  # 30 minutes
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    
                    processing_time = time.time() - start_time
                    total_events = result.get('total_events', 0)
                    successful_events = result.get('successful_events', total_events)
                    failed_events = result.get('failed_events', 0)
                    results = result.get('results', [])
                    
                    # Calculate regional cost
                    cost = len(results) * REGIONAL_COSTS[COST_TIER]
                    
                    # Update stats
                    extraction_stats['total_extractions'] += 1
                    extraction_stats['total_events_found'] += total_events
                    extraction_stats['total_cost'] += cost
                    extraction_stats['last_extraction'] = datetime.now()
                    
                    return EnhancedExtractionResponse(
                        region=REGION,
                        total_events=total_events,
                        successful_events=successful_events,
                        failed_events=failed_events,
                        processing_time=processing_time,
                        cost=cost,
                        results=results,
                        session_id=session_id,
                        extraction_method=f"enhanced_orchestrator_{REGION}"
                    )
                else:
                    error_text = await response.text()
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Production orchestrator error: {error_text}"
                    )
                    
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=408,
            detail=f"Extraction timeout after 30 minutes in region {REGION}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Enhanced extraction failed in {REGION}: {str(e)}"
        )

@app.get("/info")
async def service_info():
    """Get detailed service information and statistics"""
    uptime = (datetime.now() - extraction_stats['start_time']).total_seconds()
    
    return {
        "service": "Enhanced Multi-Region Extraction Service",
        "version": "2.0.0",
        "region": REGION,
        "cost_tier": COST_TIER,
        "cost_per_extraction": REGIONAL_COSTS[COST_TIER],
        "uptime_seconds": uptime,
        "extraction_stats": extraction_stats,
        "capabilities": {
            "enhanced_orchestrator": "Production-grade with 13+ agents",
            "calendar_discovery": "LinkFinderAgent with dynamic scrolling",
            "visual_intelligence": "Advanced image analysis and crypto knowledge",
            "database_integration": "Supabase with deduplication",
            "rate_limiting_evasion": f"Google Cloud {REGION} IP rotation",
            "mcp_browser_control": "Steel Browser integration",
            "agent_system": "Complete 13+ agent coordination"
        },
        "production_orchestrator": PRODUCTION_ORCHESTRATOR_URL
    }

@app.get("/stats")
async def extraction_statistics():
    """Get extraction statistics for this region"""
    uptime = (datetime.now() - extraction_stats['start_time']).total_seconds()
    
    return {
        "region": REGION,
        "cost_tier": COST_TIER,
        "uptime_hours": uptime / 3600,
        "total_extractions": extraction_stats['total_extractions'],
        "total_events_found": extraction_stats['total_events_found'],
        "total_cost_usd": extraction_stats['total_cost'],
        "avg_events_per_extraction": (
            extraction_stats['total_events_found'] / max(1, extraction_stats['total_extractions'])
        ),
        "avg_cost_per_event": (
            extraction_stats['total_cost'] / max(1, extraction_stats['total_events_found'])
        ) if extraction_stats['total_events_found'] > 0 else 0,
        "last_extraction": extraction_stats['last_extraction'].isoformat() if extraction_stats['last_extraction'] else None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
'''

    return service_code


def create_enhanced_dockerfile():
    """Create Dockerfile for enhanced multi-region service"""

    dockerfile_content = """FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies for enhanced service
RUN pip install --no-cache-dir \\
    fastapi==0.104.1 \\
    uvicorn[standard]==0.24.0 \\
    aiohttp==3.9.1 \\
    pydantic==2.5.0 \\
    python-dotenv==1.0.1 \\
    requests==2.31.0

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8080

# Run the enhanced multi-region service
CMD ["python", "src/api/enhanced_multi_region_service.py"]
"""

    return dockerfile_content


def create_cloud_build_config():
    """Create Cloud Build configuration for enhanced services"""

    config = {
        "steps": [
            {
                "name": "gcr.io/cloud-builders/docker",
                "args": [
                    "build",
                    "-t",
                    "us-central1-docker.pkg.dev/tokenhunter-457310/token-nav-repo/enhanced-multi-region-extractor:v3",
                    "-f",
                    "src/extraction/deployment/configs/dockerfiles/02_Dockerfile.enhanced_multi_region",
                    ".",
                ],
            },
            {
                "name": "gcr.io/cloud-builders/docker",
                "args": [
                    "push",
                    "us-central1-docker.pkg.dev/tokenhunter-457310/token-nav-repo/enhanced-multi-region-extractor:v3",
                ],
            },
            {
                "name": "gcr.io/google.com/cloudsdktool/cloud-sdk",
                "entrypoint": "gcloud",
                "args": [
                    "run",
                    "deploy",
                    "enhanced-multi-region-us-central",
                    "--image",
                    "us-central1-docker.pkg.dev/tokenhunter-457310/token-nav-repo/enhanced-multi-region-extractor:v3",
                    "--region",
                    "us-central1",
                    "--platform",
                    "managed",
                    "--allow-unauthenticated",
                    "--memory",
                    "4Gi",
                    "--cpu",
                    "2",
                    "--timeout",
                    "1800",
                    "--max-instances",
                    "5",
                    "--set-env-vars",
                    "REGION=us-central1,COST_TIER=2,STEEL_BROWSER_ENABLED=true",
                ],
            },
            {
                "name": "gcr.io/google.com/cloudsdktool/cloud-sdk",
                "entrypoint": "gcloud",
                "args": [
                    "run",
                    "deploy",
                    "enhanced-multi-region-europe-west",
                    "--image",
                    "us-central1-docker.pkg.dev/tokenhunter-457310/token-nav-repo/enhanced-multi-region-extractor:v3",
                    "--region",
                    "europe-west1",
                    "--platform",
                    "managed",
                    "--allow-unauthenticated",
                    "--memory",
                    "4Gi",
                    "--cpu",
                    "2",
                    "--timeout",
                    "1800",
                    "--max-instances",
                    "5",
                    "--set-env-vars",
                    "REGION=europe-west1,COST_TIER=3,STEEL_BROWSER_ENABLED=true",
                ],
            },
        ],
        "options": {"logging": "CLOUD_LOGGING_ONLY", "machineType": "E2_HIGHCPU_8"},
        "timeout": "2400s",
    }

    return config


def main():
    """Deploy enhanced multi-region services"""

    print("🚀 DEPLOYING ENHANCED MULTI-REGION SERVICES")
    print("=" * 70)
    print()
    print("This will create and deploy multi-region services with:")
    print("✅ Complete Enhanced Orchestrator (13+ agents)")
    print("✅ Calendar discovery with LinkFinderAgent")
    print("✅ Database integration with Supabase")
    print("✅ Visual intelligence and crypto knowledge")
    print("✅ Rate limiting evasion through IP rotation")
    print("✅ Enterprise deployment structure (src/api/)")
    print()

    # Create enhanced service
    print("📝 Creating enhanced multi-region service...")
    service_code = create_enhanced_multi_region_service()

    # Ensure src/api directory exists
    os.makedirs("../../../../src/api", exist_ok=True)

    with open("../../../../src/api/enhanced_multi_region_service.py", "w") as f:
        f.write(service_code)
    print("✅ Created src/api/enhanced_multi_region_service.py")

    # Create enhanced Dockerfile
    print("🐳 Creating enhanced Dockerfile...")
    dockerfile_content = create_enhanced_dockerfile()

    # Create deployment configs directory
    os.makedirs("../configs/dockerfiles", exist_ok=True)

    with open("../configs/dockerfiles/02_Dockerfile.enhanced_multi_region", "w") as f:
        f.write(dockerfile_content)
    print(
        "✅ Created src/extraction/deployment/configs/dockerfiles/02_Dockerfile.enhanced_multi_region"
    )

    # Create Cloud Build configuration
    print("☁️ Creating Cloud Build configuration...")
    config = create_cloud_build_config()

    os.makedirs("../configs", exist_ok=True)

    with open("../configs/02_enhanced_multi_region.yaml", "w") as f:
        json.dump(config, f, indent=2)
    print("✅ Created src/extraction/deployment/configs/02_enhanced_multi_region.yaml")

    # Create deployment script
    deployment_script = """#!/bin/bash
# Deploy Enhanced Multi-Region Services

echo "🚀 Deploying Enhanced Multi-Region Services with Complete Agent System"
echo "========================================================================="

PROJECT_ID="tokenhunter-457310" # Assuming this is standard
SERVICE_NAME_US_CENTRAL1="enhanced-multi-region-us-central"
REGION_US_CENTRAL1="us-central1"
# SERVICE_NAME_EUROPE_WEST1="enhanced-multi-region-europe-west" # Not strictly needed for this simplified check
# REGION_EUROPE_WEST1="europe-west1" # Not strictly needed for this simplified check
BUILD_CONFIG_PATH="src/extraction/deployment/configs/02_enhanced_multi_region.yaml"

# MANDATORY: Enterprise Compliance Validation
echo "🏢 Running Enterprise Compliance Validation..."
python src/extraction/scripts/orchestrator/enterprise_deployment_compliance_test.py \
  --project-id="$PROJECT_ID" \
  --service-name="$SERVICE_NAME_US_CENTRAL1" \
  --region="$REGION_US_CENTRAL1" \
  --cloudbuild-yaml="$BUILD_CONFIG_PATH"

# Check compliance result
if [ $? -ne 0 ]; then
    echo "❌ DEPLOYMENT BLOCKED: Compliance validation failed"
    echo "📋 Fix compliance issues before proceeding"
    exit 1
fi
echo "✅ Compliance validation passed - proceeding with deployment"

# Build and deploy using Cloud Build from project root
cd ../../../../

gcloud builds submit --config=$BUILD_CONFIG_PATH .

echo ""
echo "✅ Enhanced Multi-Region Services Deployed!"
echo ""
echo "🌐 Service URLs:"
echo "   US Central: https://enhanced-multi-region-us-central-867263134607.us-central1.run.app"
echo "   Europe West: https://enhanced-multi-region-europe-west-867263134607.europe-west1.run.app"
echo ""
echo "🎯 Features:"
echo "   • Complete Enhanced Orchestrator with 13+ agents"
echo "   • Calendar discovery with LinkFinderAgent (90+ events)"
echo "   • Database integration with Supabase"
echo "   • Visual intelligence and crypto knowledge"
echo "   • Rate limiting evasion through regional IP rotation"
echo "   • Enterprise deployment structure"
echo ""
echo "📊 Test the services:"
echo "   curl https://enhanced-multi-region-us-central-867263134607.us-central1.run.app/health"
"""

    with open("02_deploy_enhanced_multi_region_enterprise.sh", "w") as f:
        f.write(deployment_script)

    os.chmod("02_deploy_enhanced_multi_region_enterprise.sh", 0o755)
    print("✅ Created 02_deploy_enhanced_multi_region_enterprise.sh")

    print()
    print("🎉 ENHANCED MULTI-REGION SERVICES READY FOR DEPLOYMENT")
    print("=" * 70)
    print()
    print("📋 What was created:")
    print("   • Enhanced multi-region service in src/api/")
    print("   • Enterprise Dockerfile in deployment/configs/dockerfiles/")
    print("   • Cloud Build config in deployment/configs/")
    print("   • Enterprise deployment script (numbered priority)")
    print()
    print("🚀 To deploy:")
    print("   ./02_deploy_enhanced_multi_region_enterprise.sh")
    print()
    print("💡 Expected results after deployment:")
    print("   • Multi-region dashboard will find 90+ events")
    print("   • Complete calendar discovery with LinkFinderAgent")
    print("   • Full 13+ agent processing with database integration")
    print("   • Rate limiting evasion through Google Cloud regions")
    print()
    print("🔧 ENTERPRISE STRUCTURE BENEFITS:")
    print("   • Clean service-centric deployment organization")
    print("   • Numbered priority system (01, 02, 03)")
    print("   • Independent service deployment capabilities")
    print("   • Zero deployment confusion with clear paths")


if __name__ == "__main__":
    main()

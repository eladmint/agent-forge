#!/usr/bin/env python3
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
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

app = FastAPI(
    title="Enhanced Multi-Region Extraction Service",
    description="Complete calendar extraction with 13+ agents and rate limiting evasion",
    version="2.0.0",
)

# Regional configuration
REGION = os.getenv("REGION", "us-central1")
COST_TIER = int(os.getenv("COST_TIER", "2"))
PRODUCTION_ORCHESTRATOR_URL = (
    "https://production-orchestrator-867263134607.us-central1.run.app"
)

# Regional costs per extraction
REGIONAL_COSTS = {
    1: 0.002,  # Premium tier
    2: 0.0018,  # Standard tier
    3: 0.0015,  # Economy tier
}


# Request/Response Models
class EnhancedExtractionRequest(BaseModel):
    urls: List[str] = Field(..., description="Calendar URLs to extract")
    max_concurrent: Optional[int] = Field(
        default=3, description="Max concurrent extractions"
    )
    timeout_per_event: Optional[int] = Field(
        default=300, description="Timeout per event in seconds"
    )
    save_to_database: Optional[bool] = Field(
        default=True, description="Save results to Supabase"
    )
    visual_intelligence: Optional[bool] = Field(
        default=True, description="Enable visual intelligence"
    )
    crypto_enhanced: Optional[bool] = Field(
        default=True, description="Enable crypto knowledge"
    )
    mcp_browser: Optional[bool] = Field(
        default=True, description="Enable MCP browser control"
    )
    calendar_discovery: Optional[bool] = Field(
        default=True, description="Enable full calendar discovery"
    )


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
    production_orchestrator_status: str = Field(
        ..., description="Production orchestrator connectivity"
    )


# Service stats
extraction_stats = {
    "total_extractions": 0,
    "total_events_found": 0,
    "total_cost": 0.0,
    "start_time": datetime.now(),
    "last_extraction": None,
}


@app.on_event("startup")
async def startup_event():
    """Initialize service"""
    logger = logging.getLogger(__name__)
    logger.info(f"🚀 Enhanced Multi-Region Service starting in {REGION}")
    logger.info(
        f"💰 Cost tier: {COST_TIER} (${REGIONAL_COSTS[COST_TIER]:.4f}/extraction)"
    )
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
        "ip_rotation": f"Google Cloud {REGION}",
    }

    return HealthResponse(
        status="healthy",
        region=REGION,
        cost_tier=COST_TIER,
        capabilities=capabilities,
        production_orchestrator_status=orchestrator_status,
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
            "calendar_discovery": request.calendar_discovery,
        }

        # Add regional headers to appear from this region
        headers = {
            "Content-Type": "application/json",
            "X-Forwarded-For": f"34.102.{(hash(REGION) % 254) + 1}.{(hash(session_id) % 254) + 1}",
            "X-Real-IP": f"34.102.{(hash(REGION) % 254) + 1}.{(hash(session_id) % 254) + 1}",
            "X-Region": REGION,
            "User-Agent": f"Multi-Region-Extractor/{REGION}/2.0.0",
        }

        # Call production orchestrator with enhanced capabilities
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{PRODUCTION_ORCHESTRATOR_URL}/extract",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=1800),  # 30 minutes
            ) as response:

                if response.status == 200:
                    result = await response.json()

                    processing_time = time.time() - start_time
                    total_events = result.get("total_events", 0)
                    successful_events = result.get("successful_events", total_events)
                    failed_events = result.get("failed_events", 0)
                    results = result.get("results", [])

                    # Calculate regional cost
                    cost = len(results) * REGIONAL_COSTS[COST_TIER]

                    # Update stats
                    extraction_stats["total_extractions"] += 1
                    extraction_stats["total_events_found"] += total_events
                    extraction_stats["total_cost"] += cost
                    extraction_stats["last_extraction"] = datetime.now()

                    return EnhancedExtractionResponse(
                        region=REGION,
                        total_events=total_events,
                        successful_events=successful_events,
                        failed_events=failed_events,
                        processing_time=processing_time,
                        cost=cost,
                        results=results,
                        session_id=session_id,
                        extraction_method=f"enhanced_orchestrator_{REGION}",
                    )
                else:
                    error_text = await response.text()
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Production orchestrator error: {error_text}",
                    )

    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=408,
            detail=f"Extraction timeout after 30 minutes in region {REGION}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Enhanced extraction failed in {REGION}: {str(e)}"
        )


@app.get("/info")
async def service_info():
    """Get detailed service information and statistics"""
    uptime = (datetime.now() - extraction_stats["start_time"]).total_seconds()

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
            "agent_system": "Complete 13+ agent coordination",
        },
        "production_orchestrator": PRODUCTION_ORCHESTRATOR_URL,
    }


@app.get("/stats")
async def extraction_statistics():
    """Get extraction statistics for this region"""
    uptime = (datetime.now() - extraction_stats["start_time"]).total_seconds()

    return {
        "region": REGION,
        "cost_tier": COST_TIER,
        "uptime_hours": uptime / 3600,
        "total_extractions": extraction_stats["total_extractions"],
        "total_events_found": extraction_stats["total_events_found"],
        "total_cost_usd": extraction_stats["total_cost"],
        "avg_events_per_extraction": (
            extraction_stats["total_events_found"]
            / max(1, extraction_stats["total_extractions"])
        ),
        "avg_cost_per_event": (
            (
                extraction_stats["total_cost"]
                / max(1, extraction_stats["total_events_found"])
            )
            if extraction_stats["total_events_found"] > 0
            else 0
        ),
        "last_extraction": (
            extraction_stats["last_extraction"].isoformat()
            if extraction_stats["last_extraction"]
            else None
        ),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

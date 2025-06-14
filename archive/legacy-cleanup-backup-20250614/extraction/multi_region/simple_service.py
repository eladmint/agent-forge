#!/usr/bin/env python3
"""
🌐 Simple Multi-Region Extraction Service - Testing POC
This is a simplified version for testing multi-region deployment functionality.
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
REGION = os.getenv("REGION", "us-central1")
REGION_ID = os.getenv("REGION_ID", "us")
COST_TIER = int(os.getenv("COST_TIER", "2"))
EXTRACTION_MODE = os.getenv("EXTRACTION_MODE", "test")

# Regional cost configuration (cost per extraction in USD)
REGIONAL_COSTS = {
    1: 0.0015,  # Tier 1 - Asia (cheapest)
    2: 0.0018,  # Tier 2 - US (moderate)
    3: 0.0020,  # Tier 3 - Europe (most expensive)
}

# Regional capabilities
REGIONAL_CAPABILITIES = {
    "us-central1": {
        "steel_browser": True,
        "max_concurrent": 8,
        "ip_ranges": ["34.102.0.0/16", "34.104.0.0/16"],
        "timezone": "America/Chicago",
    },
    "europe-west1": {
        "steel_browser": True,
        "max_concurrent": 6,
        "ip_ranges": ["34.76.0.0/16", "34.78.0.0/16"],
        "timezone": "Europe/London",
    },
    "asia-southeast1": {
        "steel_browser": True,
        "max_concurrent": 4,
        "ip_ranges": ["34.126.0.0/16", "34.128.0.0/16"],
        "timezone": "Asia/Singapore",
    },
}


# Request/Response Models
class ExtractionRequest(BaseModel):
    urls: List[str] = Field(..., description="URLs to extract data from")
    options: Optional[Dict[str, Any]] = Field(
        default={}, description="Extraction options"
    )
    budget: Optional[float] = Field(default=1.0, description="Budget limit in USD")
    mode: Optional[str] = Field(default="standard", description="Extraction mode")


class ExtractionResponse(BaseModel):
    region: str = Field(..., description="Processing region")
    cost: float = Field(..., description="Extraction cost in USD")
    results: List[Dict[str, Any]] = Field(..., description="Extraction results")
    processing_time: float = Field(..., description="Processing time in seconds")
    source_ips: List[str] = Field(..., description="Source IP ranges used")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service health status")
    region: str = Field(..., description="Service region")
    capabilities: Dict[str, Any] = Field(..., description="Regional capabilities")
    cost_tier: int = Field(..., description="Cost tier for this region")


# FastAPI App
app = FastAPI(
    title="Multi-Region Token Event Extraction Service",
    description="Distributed extraction service for rate limiting evasion",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Global state
extraction_stats = {
    "total_extractions": 0,
    "total_cost": 0.0,
    "start_time": datetime.utcnow(),
}


@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    logger.info(f"🚀 Multi-Region Extraction Service starting in region: {REGION}")
    logger.info(
        f"💰 Cost tier: {COST_TIER} (${REGIONAL_COSTS[COST_TIER]:.4f} per extraction)"
    )
    logger.info(f"🎯 Extraction mode: {EXTRACTION_MODE}")

    capabilities = REGIONAL_CAPABILITIES.get(REGION, {})
    logger.info(f"🔧 Regional capabilities: {capabilities}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info(f"🛑 Multi-Region Extraction Service shutting down in region: {REGION}")
    logger.info(f"📊 Final stats: {extraction_stats}")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with regional information"""
    capabilities = REGIONAL_CAPABILITIES.get(REGION, {})

    return HealthResponse(
        status="healthy", region=REGION, capabilities=capabilities, cost_tier=COST_TIER
    )


@app.get("/info")
async def service_info():
    """Get detailed service information"""
    capabilities = REGIONAL_CAPABILITIES.get(REGION, {})
    uptime = (datetime.utcnow() - extraction_stats["start_time"]).total_seconds()

    return {
        "service": "Multi-Region Token Event Extraction Service",
        "version": "1.0.0",
        "region": REGION,
        "region_id": REGION_ID,
        "cost_tier": COST_TIER,
        "cost_per_extraction": REGIONAL_COSTS[COST_TIER],
        "extraction_mode": EXTRACTION_MODE,
        "capabilities": capabilities,
        "stats": {
            **extraction_stats,
            "uptime_seconds": uptime,
            "average_cost_per_extraction": (
                extraction_stats["total_cost"]
                / max(extraction_stats["total_extractions"], 1)
            ),
        },
    }


@app.post("/extract", response_model=ExtractionResponse)
async def extract_events(request: ExtractionRequest):
    """Extract events from URLs using regional capabilities"""
    start_time = datetime.utcnow()

    # Validate budget
    estimated_cost = len(request.urls) * REGIONAL_COSTS[COST_TIER]
    if estimated_cost > request.budget:
        raise HTTPException(
            status_code=400,
            detail=f"Estimated cost ${estimated_cost:.4f} exceeds budget ${request.budget:.4f}",
        )

    # Simulate extraction process
    logger.info(f"🔄 Processing {len(request.urls)} URLs in region {REGION}")

    results = []
    total_cost = 0.0

    for url in request.urls:
        # Simulate extraction
        await asyncio.sleep(0.1)  # Simulate processing time

        result = {
            "url": url,
            "region": REGION,
            "status": "success",
            "events_found": 3,  # Simulated
            "extraction_method": "http",  # Simplified for testing
            "processing_time": 0.1,
            "timestamp": datetime.utcnow().isoformat(),
        }

        results.append(result)
        total_cost += REGIONAL_COSTS[COST_TIER]

    # Update global stats
    extraction_stats["total_extractions"] += len(request.urls)
    extraction_stats["total_cost"] += total_cost

    processing_time = (datetime.utcnow() - start_time).total_seconds()
    capabilities = REGIONAL_CAPABILITIES.get(REGION, {})

    logger.info(
        f"✅ Completed extraction: {len(results)} results, ${total_cost:.4f} cost"
    )

    return ExtractionResponse(
        region=REGION,
        cost=total_cost,
        results=results,
        processing_time=processing_time,
        source_ips=capabilities.get("ip_ranges", []),
    )


@app.get("/regions")
async def list_regions():
    """List all available regions and their capabilities"""
    return {
        "current_region": REGION,
        "available_regions": REGIONAL_CAPABILITIES,
        "cost_tiers": REGIONAL_COSTS,
    }


@app.get("/stats")
async def get_stats():
    """Get service statistics"""
    uptime = (datetime.utcnow() - extraction_stats["start_time"]).total_seconds()

    return {
        "region": REGION,
        "stats": extraction_stats,
        "uptime_seconds": uptime,
        "cost_efficiency": {
            "cost_per_extraction": REGIONAL_COSTS[COST_TIER],
            "total_extractions": extraction_stats["total_extractions"],
            "total_cost": extraction_stats["total_cost"],
            "average_cost": (
                extraction_stats["total_cost"]
                / max(extraction_stats["total_extractions"], 1)
            ),
        },
    }


if __name__ == "__main__":
    # Run the service
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(
        "simple_multi_region_service:app", host="0.0.0.0", port=port, log_level="info"
    )

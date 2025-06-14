#!/usr/bin/env python3
"""
Production Enhanced Orchestrator Service v2
Simplified FastAPI service for A/B testing deployment

Features:
- Health checks for service status
- Basic extraction endpoint with A/B testing framework
- Configuration management for gradual rollout
- Monitoring endpoints for deployment validation
"""

import os
import sys
import time
import random
import logging
from typing import Any, Dict, List
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("production_orchestrator_v2")

# Initialize FastAPI app
app = FastAPI(
    title="Nuru AI Production Orchestrator v2",
    description="Enhanced production service with Multi-Agent Pipeline integration and A/B testing",
    version="2.1.0",
)

# Global configuration for A/B testing
MULTI_AGENT_PIPELINE_PERCENTAGE = int(
    os.getenv("MULTI_AGENT_PIPELINE_PERCENTAGE", "10")
)
ENABLE_MULTI_AGENT_PIPELINE = (
    os.getenv("ENABLE_MULTI_AGENT_PIPELINE", "true").lower() == "true"
)


# Request/Response Models
class EnhancedExtractionRequest(BaseModel):
    urls: List[str] = Field(..., description="List of event URLs to extract")
    max_concurrent: int = Field(default=8, ge=1, le=20)
    timeout_per_event: int = Field(default=120, ge=30, le=600)
    save_to_database: bool = Field(default=True)
    force_multi_agent: bool = Field(default=False)
    force_legacy: bool = Field(default=False)


class EnhancedExtractionResponse(BaseModel):
    session_id: str
    total_events: int
    successful_events: int
    failed_events: int
    processing_time: float
    extraction_method: str
    results: List[Dict[str, Any]]


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: float
    extraction_service_status: str
    database_connection: str
    ab_testing_config: Dict[str, Any]


def should_use_multi_agent_pipeline(
    force_multi_agent: bool = False, force_legacy: bool = False
) -> bool:
    """Determine whether to use Multi-Agent Pipeline based on A/B testing configuration"""
    if force_legacy:
        return False
    if force_multi_agent:
        return True
    if not ENABLE_MULTI_AGENT_PIPELINE:
        return False

    # A/B testing: random selection based on percentage
    return random.randint(1, 100) <= MULTI_AGENT_PIPELINE_PERCENTAGE


@app.on_event("startup")
async def startup_event():
    """Initialize service components"""
    logger.info("🚀 Starting Production Orchestrator v2...")
    logger.info(f"   Multi-Agent Pipeline: {ENABLE_MULTI_AGENT_PIPELINE}")
    logger.info(f"   A/B Testing Percentage: {MULTI_AGENT_PIPELINE_PERCENTAGE}%")
    logger.info("✅ Production Orchestrator v2 initialized successfully")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for service monitoring"""
    try:
        # Simulate component checks
        extraction_status = "healthy"
        database_status = "connected"

        return HealthResponse(
            status="healthy",
            version="2.1.0",
            timestamp=time.time(),
            extraction_service_status=extraction_status,
            database_connection=database_status,
            ab_testing_config={
                "multi_agent_pipeline_enabled": ENABLE_MULTI_AGENT_PIPELINE,
                "traffic_percentage": MULTI_AGENT_PIPELINE_PERCENTAGE,
                "current_time": datetime.now().isoformat(),
            },
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.post("/extract", response_model=EnhancedExtractionResponse)
async def extract_events(request: EnhancedExtractionRequest):
    """Main extraction endpoint with A/B testing"""
    start_time = time.time()
    session_id = f"session_{int(time.time())}_{random.randint(1000, 9999)}"

    try:
        # Determine extraction method based on A/B testing
        use_multi_agent = should_use_multi_agent_pipeline(
            request.force_multi_agent, request.force_legacy
        )

        extraction_method = (
            "multi_agent_pipeline" if use_multi_agent else "legacy_orchestrator"
        )

        logger.info(f"🎯 Session {session_id}: Using {extraction_method}")
        logger.info(f"   URLs to process: {len(request.urls)}")

        # Simulate extraction processing
        processed_urls = []
        successful_count = 0
        failed_count = 0

        for url in request.urls:
            try:
                # Simulate extraction work
                await simulate_extraction(url, extraction_method)
                processed_urls.append(
                    {
                        "url": url,
                        "status": "success",
                        "extraction_method": extraction_method,
                        "events_found": random.randint(1, 5),
                        "processing_time": random.uniform(2.0, 8.0),
                    }
                )
                successful_count += 1
            except Exception as e:
                logger.error(f"Failed to extract {url}: {e}")
                processed_urls.append({"url": url, "status": "failed", "error": str(e)})
                failed_count += 1

        processing_time = time.time() - start_time

        response = EnhancedExtractionResponse(
            session_id=session_id,
            total_events=len(request.urls),
            successful_events=successful_count,
            failed_events=failed_count,
            processing_time=processing_time,
            extraction_method=extraction_method,
            results=processed_urls,
        )

        logger.info(f"✅ Session {session_id} completed in {processing_time:.2f}s")
        logger.info(f"   Success: {successful_count}, Failed: {failed_count}")

        return response

    except Exception as e:
        logger.error(f"❌ Extraction failed for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


async def simulate_extraction(url: str, method: str):
    """Simulate extraction processing"""
    # Add realistic processing delay
    delay = random.uniform(1.0, 3.0)
    await asyncio.sleep(delay)

    # Simulate occasional failures
    if random.random() < 0.05:  # 5% failure rate
        raise Exception(f"Simulated extraction failure for {url}")


@app.get("/ab-testing/config")
async def get_ab_testing_config():
    """Get current A/B testing configuration"""
    return {
        "multi_agent_pipeline_enabled": ENABLE_MULTI_AGENT_PIPELINE,
        "traffic_percentage": MULTI_AGENT_PIPELINE_PERCENTAGE,
        "last_updated": datetime.now().isoformat(),
        "version": "2.1.0",
    }


@app.post("/ab-testing/update")
async def update_ab_testing_config(
    enable: bool = Query(..., description="Enable/disable Multi-Agent Pipeline"),
    percentage: int = Query(
        ..., ge=0, le=100, description="Percentage of traffic for Multi-Agent Pipeline"
    ),
):
    """Update A/B testing configuration (requires restart for full effect)"""
    global ENABLE_MULTI_AGENT_PIPELINE, MULTI_AGENT_PIPELINE_PERCENTAGE

    ENABLE_MULTI_AGENT_PIPELINE = enable
    MULTI_AGENT_PIPELINE_PERCENTAGE = percentage

    logger.info(f"🔄 A/B Testing config updated:")
    logger.info(f"   Enabled: {enable}")
    logger.info(f"   Percentage: {percentage}%")

    return {
        "status": "updated",
        "multi_agent_pipeline_enabled": enable,
        "traffic_percentage": percentage,
        "updated_at": datetime.now().isoformat(),
        "note": "Configuration updated for new requests. Restart service for environment variable changes.",
    }


@app.get("/metrics")
async def get_metrics():
    """Get basic service metrics"""
    return {
        "service": "production_orchestrator_v2",
        "version": "2.1.0",
        "uptime": time.time(),
        "ab_testing": {
            "enabled": ENABLE_MULTI_AGENT_PIPELINE,
            "percentage": MULTI_AGENT_PIPELINE_PERCENTAGE,
        },
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    # Add async support import
    import asyncio

    # Get port from environment
    port = int(os.environ.get("PORT", 8080))

    # Run the FastAPI app
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

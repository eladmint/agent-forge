#!/usr/bin/env python3
"""
🌐 Multi-Region Extraction Service - Cloud Run Deployment
This service runs in multiple Google Cloud regions to provide distributed extraction
capabilities with rate limiting evasion and Steel Browser integration.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extraction.agents.event_data_extractor_agent import EventDataExtractorAgent
# from mcp_tools.steel_enhanced_client import SteelEnhancedScrapingManager
# Temporary: Steel Enhanced client not available in deployment
class SteelEnhancedScrapingManager:
    """Temporary stub for SteelEnhancedScrapingManager"""
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.logger.warning("SteelEnhancedScrapingManager stub - steel browser functionality not available")
    
    async def extract_comprehensive(self, *args, **kwargs):
        return {"error": "Steel browser not available in this deployment", "events": []}

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Multi-Region Token Event Extraction Service",
    description="Distributed extraction service with Steel Browser and rate limiting evasion",
    version="2.0.0",
)


# Pydantic models for request/response
class ExtractionRequest(BaseModel):
    url: str = Field(..., description="URL to extract events from")
    method: str = Field(
        default="extract_comprehensive", description="Extraction method"
    )
    config: Dict[str, Any] = Field(
        default_factory=dict, description="Extraction configuration"
    )


class SteelExtractionRequest(BaseModel):
    url: str = Field(..., description="URL to extract with Steel Browser")
    method: str = Field(
        default="extract_comprehensive", description="Steel extraction method"
    )
    config: Dict[str, Any] = Field(
        default_factory=dict, description="Steel Browser configuration"
    )


class ExtractionResponse(BaseModel):
    status: str
    region: str
    method: str
    data: Dict[str, Any] = Field(default_factory=dict)
    meta: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str
    processing_time: float


# Global state
extraction_agent = None
steel_manager = None
region_info = {
    "name": os.getenv("CLOUD_RUN_REGION", "unknown"),
    "service": os.getenv("K_SERVICE", "multi-region-extractor"),
    "revision": os.getenv("K_REVISION", "unknown"),
}


@app.on_event("startup")
async def startup_event():
    """Initialize extraction services on startup"""
    global extraction_agent, steel_manager

    logger.info(f"🚀 Starting Multi-Region Extraction Service in {region_info['name']}")

    try:
        # Initialize EventDataExtractorAgent
        extraction_agent = EventDataExtractorAgent()
        logger.info("✅ EventDataExtractorAgent initialized")

        # Initialize Steel Browser manager if available
        try:
            steel_manager = SteelEnhancedScrapingManager()
            await steel_manager.__aenter__()
            logger.info("✅ Steel Browser manager initialized")
        except Exception as e:
            logger.warning(f"⚠️ Steel Browser unavailable: {e}")
            steel_manager = None

    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global steel_manager

    logger.info("🔄 Shutting down Multi-Region Extraction Service")

    if steel_manager:
        try:
            await steel_manager.__aexit__(None, None, None)
            logger.info("✅ Steel Browser manager closed")
        except Exception as e:
            logger.error(f"❌ Error closing Steel Browser manager: {e}")


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancer"""
    return {
        "status": "healthy",
        "region": region_info["name"],
        "service": region_info["service"],
        "revision": region_info["revision"],
        "timestamp": datetime.now().isoformat(),
        "steel_available": steel_manager is not None,
    }


@app.get("/info")
async def service_info():
    """Get detailed service information"""
    return {
        "service": "Multi-Region Token Event Extraction",
        "version": "2.0.0",
        "region": region_info,
        "capabilities": {
            "standard_extraction": True,
            "steel_browser": steel_manager is not None,
            "event_data_extraction": extraction_agent is not None,
            "anti_rate_limiting": True,
            "multi_region_support": True,
        },
        "endpoints": {
            "/extract/standard": "Standard HTTP extraction",
            "/extract/steel": "Steel Browser extraction",
            "/extract/comprehensive": "Comprehensive event extraction",
            "/health": "Health check",
            "/info": "Service information",
        },
    }


@app.post("/extract/standard", response_model=ExtractionResponse)
async def extract_standard(request: ExtractionRequest):
    """
    Standard extraction using EventDataExtractorAgent
    """
    start_time = asyncio.get_event_loop().time()

    try:
        logger.info(f"🔍 Standard extraction request for: {request.url}")

        if not extraction_agent:
            raise HTTPException(
                status_code=503, detail="Extraction agent not available"
            )

        # Use EventDataExtractorAgent for extraction
        result = await extraction_agent.extract_events_from_url(request.url)

        if not result.get("success", False):
            raise HTTPException(
                status_code=(
                    429 if "rate limit" in str(result.get("error", "")).lower() else 500
                ),
                detail=f"Extraction failed: {result.get('error', 'Unknown error')}",
            )

        processing_time = asyncio.get_event_loop().time() - start_time

        return ExtractionResponse(
            status="success",
            region=region_info["name"],
            method="standard",
            data=result,
            meta={
                "events_found": len(result.get("events", [])),
                "processing_region": region_info["name"],
                "user_agent": request.config.get("headers", {}).get(
                    "User-Agent", "default"
                ),
            },
            timestamp=datetime.now().isoformat(),
            processing_time=processing_time,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Standard extraction error: {e}")
        processing_time = asyncio.get_event_loop().time() - start_time

        # Check for rate limiting indicators
        error_msg = str(e).lower()
        if any(
            indicator in error_msg
            for indicator in ["rate limit", "429", "too many requests", "blocked"]
        ):
            raise HTTPException(status_code=429, detail=f"Rate limited: {str(e)}")

        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@app.post("/extract/steel", response_model=ExtractionResponse)
async def extract_steel(request: SteelExtractionRequest):
    """
    Steel Browser extraction with enterprise features
    """
    start_time = asyncio.get_event_loop().time()

    try:
        logger.info(f"🤖 Steel Browser extraction request for: {request.url}")

        if not steel_manager:
            raise HTTPException(status_code=503, detail="Steel Browser not available")

        # Configure Steel Browser extraction
        selectors = {
            "event_links": "a.event-link.content-link",
            "event_titles": "h3.text-lg.font-semibold",
            "event_dates": "time",
            "event_locations": "[data-testid='event-location']",
            "pagination": "button[aria-label*='Next']",
        }

        # Execute Steel Browser extraction
        result = await steel_manager.scrape_with_intelligence(
            request.url, selectors=selectors, max_retries=2
        )

        if result.get("status") != "Success":
            error_msg = result.get("error", "Unknown Steel Browser error")

            # Check for rate limiting
            if any(
                indicator in error_msg.lower()
                for indicator in ["rate limit", "429", "blocked", "captcha"]
            ):
                raise HTTPException(
                    status_code=429, detail=f"Steel Browser rate limited: {error_msg}"
                )

            raise HTTPException(
                status_code=500, detail=f"Steel Browser extraction failed: {error_msg}"
            )

        processing_time = asyncio.get_event_loop().time() - start_time

        # Extract Steel Browser specific metadata
        steel_data = result.get("data", {})
        navigation_info = result.get("navigation", {})

        return ExtractionResponse(
            status="success",
            region=region_info["name"],
            method="steel_browser",
            data={
                "content": steel_data,
                "events": steel_data.get("events", []),
                "extracted_elements": steel_data.get("elements", {}),
                "page_info": steel_data.get("page_info", {}),
            },
            meta={
                "steel_tier": result.get("tier", "Steel Browser Enhanced"),
                "captcha_solved": navigation_info.get("captchaDetected", False),
                "js_rendered": True,
                "anti_detection": True,
                "proxy_used": steel_data.get("proxy_info"),
                "processing_region": region_info["name"],
                "browser_fingerprint": steel_data.get("fingerprint_info"),
            },
            timestamp=datetime.now().isoformat(),
            processing_time=processing_time,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Steel Browser extraction error: {e}")
        processing_time = asyncio.get_event_loop().time() - start_time

        # Check for rate limiting indicators
        error_msg = str(e).lower()
        if any(
            indicator in error_msg
            for indicator in ["rate limit", "429", "too many requests", "blocked"]
        ):
            raise HTTPException(
                status_code=429, detail=f"Steel Browser rate limited: {str(e)}"
            )

        raise HTTPException(
            status_code=500, detail=f"Steel Browser extraction failed: {str(e)}"
        )


@app.post("/extract/comprehensive", response_model=ExtractionResponse)
async def extract_comprehensive(request: ExtractionRequest):
    """
    Comprehensive extraction with fallback strategy:
    1. Try Steel Browser first (if available)
    2. Fallback to standard extraction
    3. Provide detailed analysis and recommendations
    """
    start_time = asyncio.get_event_loop().time()

    try:
        logger.info(f"🔄 Comprehensive extraction request for: {request.url}")

        result = None
        method_used = "none"
        fallback_used = False

        # Strategy 1: Try Steel Browser first
        if steel_manager:
            try:
                logger.info("🤖 Attempting Steel Browser extraction...")
                steel_request = SteelExtractionRequest(
                    url=request.url, method=request.method, config=request.config
                )
                result = await extract_steel(steel_request)
                method_used = "steel_browser"
                logger.info("✅ Steel Browser extraction successful")

            except HTTPException as e:
                if e.status_code == 429:
                    logger.warning("⚠️ Steel Browser rate limited, trying fallback...")
                    fallback_used = True
                else:
                    logger.error(f"❌ Steel Browser failed: {e.detail}")
                    fallback_used = True
            except Exception as e:
                logger.error(f"❌ Steel Browser error: {e}")
                fallback_used = True
        else:
            logger.info("⚠️ Steel Browser not available, using standard extraction")
            fallback_used = True

        # Strategy 2: Fallback to standard extraction
        if fallback_used and not result:
            try:
                logger.info("🔍 Attempting standard extraction...")
                result = await extract_standard(request)
                method_used = "standard_fallback" if fallback_used else "standard"
                logger.info("✅ Standard extraction successful")

            except HTTPException as e:
                if e.status_code == 429:
                    logger.error(
                        "❌ Both Steel Browser and standard extraction rate limited"
                    )
                    raise HTTPException(
                        status_code=429,
                        detail="All extraction methods rate limited in this region",
                    )
                raise

        if not result:
            raise HTTPException(status_code=500, detail="All extraction methods failed")

        # Enhance result with comprehensive metadata
        processing_time = asyncio.get_event_loop().time() - start_time

        comprehensive_meta = {
            **result.meta,
            "extraction_strategy": {
                "primary_method": "steel_browser" if steel_manager else "standard",
                "method_used": method_used,
                "fallback_triggered": fallback_used,
                "steel_available": steel_manager is not None,
            },
            "region_info": region_info,
            "comprehensive_processing_time": processing_time,
            "recommendation": {
                "next_extraction": (
                    "Use different region"
                    if method_used.endswith("_fallback")
                    else "Continue with current region"
                ),
                "rate_limit_status": (
                    "Likely rate limited" if fallback_used else "Operating normally"
                ),
            },
        }

        return ExtractionResponse(
            status=result.status,
            region=result.region,
            method=f"comprehensive_{method_used}",
            data=result.data,
            meta=comprehensive_meta,
            timestamp=datetime.now().isoformat(),
            processing_time=processing_time,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Comprehensive extraction error: {e}")
        processing_time = asyncio.get_event_loop().time() - start_time

        raise HTTPException(
            status_code=500, detail=f"Comprehensive extraction failed: {str(e)}"
        )


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler with detailed error info"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "region": region_info["name"],
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url),
            "suggestion": {
                429: "Try different region or wait before retrying",
                503: "Service temporarily unavailable, try another region",
                500: "Internal error, check logs or try alternative method",
            }.get(exc.status_code, "Check request parameters and try again"),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler"""
    logger.error(f"❌ Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "region": region_info["name"],
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url),
        },
    )


# Main execution
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"🚀 Starting Multi-Region Extraction Service on {host}:{port}")
    logger.info(f"🌐 Region: {region_info['name']}")

    uvicorn.run(app, host=host, port=port, log_level="info", access_log=True)

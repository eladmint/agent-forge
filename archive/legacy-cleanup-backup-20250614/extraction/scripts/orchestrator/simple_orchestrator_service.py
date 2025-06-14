#!/usr/bin/env python3
"""
Simple Enhanced Orchestrator Service - Test Version
Basic FastAPI service to test deployment without heavy dependencies
"""

import logging
import os
import time

from fastapi import FastAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Nuru AI Enhanced Orchestrator Service - Test",
    description="Test service for Enhanced Orchestrator deployment",
    version="1.0.0-test",
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Enhanced Orchestrator Service - Test",
        "status": "healthy",
        "version": "1.0.0-test",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        return {
            "status": "healthy",
            "version": "1.0.0-test",
            "timestamp": time.time(),
            "environment": os.getenv("LOG_LEVEL", "production"),
            "service": "enhanced-orchestrator-test",
            "ready": True,
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e), "timestamp": time.time()}


@app.post("/test")
async def test_endpoint():
    """Test endpoint for deployment validation"""
    return {
        "message": "Enhanced Orchestrator test successful",
        "timestamp": time.time(),
        "status": "operational",
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

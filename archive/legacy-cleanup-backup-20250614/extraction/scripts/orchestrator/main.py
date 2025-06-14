#!/usr/bin/env python3
"""
Main entry point for the enhanced orchestrator service.
This script runs the production enhanced orchestrator service.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
sys.path.insert(0, project_root)

# Import the FastAPI app for gunicorn
from extraction.scripts.orchestrator.production_enhanced_orchestrator_service import app

# For gunicorn compatibility
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
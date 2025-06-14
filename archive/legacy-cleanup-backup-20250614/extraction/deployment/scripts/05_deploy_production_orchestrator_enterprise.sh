#!/bin/bash

# DEPLOYMENT SCRIPT: 05 - Production Orchestrator Enterprise
# STATUS: ✅ PRIMARY RECOMMENDED
# ARCHITECTURE: Production Enhanced Orchestrator with Validation Fix
# USE WHEN: Deploying Production Orchestrator with validation bypass logic

set -e

echo "🚀 ENTERPRISE DEPLOYMENT: Production Orchestrator with Validation Fix"
echo "📍 Deploying to: us-central1"
echo "🔧 Using: Enterprise Cloud Build configuration"
echo

# Ensure we're in the project root
cd "$(dirname "$0")/../../../.."

# Verify validation fix is present
echo "🔍 Verifying validation fix is present..."
if grep -q "CRITICAL FIX: Add calendar extraction metadata for validation bypass" extraction/main_extractor.py; then
    echo "✅ Validation fix confirmed in extraction/main_extractor.py"
else
    echo "❌ Validation fix NOT found in extraction/main_extractor.py"
    exit 1
fi

# Execute enterprise deployment using Cloud Build
echo "🏗️ Executing enterprise deployment..."
echo "📁 Build Context: $(pwd)"
echo "📋 Config: src/extraction/deployment/configs/04_production_orchestrator.yaml"
echo

gcloud builds submit \
    --config=src/extraction/deployment/configs/04_production_orchestrator.yaml \
    --region=us-central1 \
    .

echo
echo "✅ ENTERPRISE DEPLOYMENT COMPLETE"
echo "🌐 Service: production-orchestrator"
echo "📍 Region: us-central1"
echo "🔧 Validation Fix: DEPLOYED"
echo
echo "🧪 Next Steps:"
echo "1. Verify service health: curl https://production-orchestrator-oo6mrfxexq-uc.a.run.app/health"
echo "2. Test validation bypass with calendar extraction"
echo "3. Check Enhanced Multi-Region Services now use updated orchestrator" 
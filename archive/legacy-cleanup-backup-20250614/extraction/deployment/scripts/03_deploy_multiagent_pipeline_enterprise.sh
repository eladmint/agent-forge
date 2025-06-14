#!/bin/bash
# Enterprise Deployment Script for Multi-Agent Pipeline
# Deploys Enhanced Multi-Region Services with Full Multi-Agent Pipeline Support
# Following PROJECT_STRUCTURE_STANDARDS compliance

set -e

echo "🚀 Enterprise Multi-Agent Pipeline Deployment"
echo "=============================================="
echo "📋 Following PROJECT_STRUCTURE_STANDARDS enterprise deployment process"
echo "🎯 Target: Deploy Multi-Agent Pipeline with 13+ specialized agents"
echo "🔧 Architecture: Enhanced Multi-Region with Steel Browser integration"
echo ""

# Validate we're in the correct directory (project root)
if [ ! -f "requirements.txt" ] || [ ! -d "src/extraction" ]; then
    echo "❌ Error: Must run from project root directory"
    echo "💡 Current directory: $(pwd)"
    echo "💡 Expected files: requirements.txt, src/extraction/"
    exit 1
fi

echo "✅ Project structure validated"
echo "📁 Current directory: $(pwd)"

# Validate Multi-Agent Pipeline service exists
if [ ! -f "src/extraction/scripts/orchestrator/production_enhanced_orchestrator_service.py" ]; then
    echo "❌ Error: Multi-Agent Pipeline service not found"
    echo "💡 Expected: src/extraction/scripts/orchestrator/production_enhanced_orchestrator_service.py"
    exit 1
fi

echo "✅ Multi-Agent Pipeline service file validated"

# Validate specialized agents exist
if [ ! -d "src/extraction/agents/specialized" ]; then
    echo "❌ Error: Specialized agents directory not found"
    echo "💡 Expected: src/extraction/agents/specialized/"
    exit 1
fi

AGENT_COUNT=$(ls src/extraction/agents/specialized/*.py | wc -l)
echo "✅ Specialized agents validated: $AGENT_COUNT agents found"

# Validate Cloud Build config exists
if [ ! -f "src/extraction/deployment/configs/03_enhanced_multi_region_multiagent.yaml" ]; then
    echo "❌ Error: Multi-Agent Pipeline Cloud Build config not found"
    echo "💡 Expected: src/extraction/deployment/configs/03_enhanced_multi_region_multiagent.yaml"
    exit 1
fi

echo "✅ Cloud Build configuration validated"

# Validate Dockerfile exists
if [ ! -f "src/extraction/deployment/configs/dockerfiles/03_Dockerfile.multiagent_pipeline" ]; then
    echo "❌ Error: Multi-Agent Pipeline Dockerfile not found"
    echo "💡 Expected: src/extraction/deployment/configs/dockerfiles/03_Dockerfile.multiagent_pipeline"
    exit 1
fi

echo "✅ Multi-Agent Pipeline Dockerfile validated"

echo ""
echo "🔧 Pre-deployment Configuration:"
echo "   📦 Image: enhanced-multi-region-extractor:v4-multiagent"
echo "   🌐 Regions: us-central1, europe-west1"
echo "   🤖 Agents: 13+ specialized agents"
echo "   🛡️ Features: Steel Browser, Visual Intelligence, Quality Optimization"
echo ""

# Confirm deployment
echo "🚨 Ready to deploy Multi-Agent Pipeline to production?"
echo "   This will update the enhanced-multi-region services with:"
echo "   • Full Multi-Agent Pipeline (13+ agents)"
echo "   • Enhanced Scroll Agent for 100% event discovery"
echo "   • Link Discovery Agent for 95% URL discovery"
echo "   • Text Extraction Agent for 90% field completion"
echo "   • Quality Optimization Agent"
echo "   • Steel Browser integration"
echo ""
read -p "Continue with deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

echo ""
echo "🚀 Starting Multi-Agent Pipeline deployment..."
echo "⏱️  Estimated time: 8-12 minutes"
echo ""

# Execute Cloud Build deployment
echo "📦 Building and deploying Multi-Agent Pipeline..."
gcloud builds submit \
    --config=src/extraction/deployment/configs/03_enhanced_multi_region_multiagent.yaml \
    --timeout=3600 \
    .

BUILD_RESULT=$?

if [ $BUILD_RESULT -eq 0 ]; then
    echo ""
    echo "🎉 Multi-Agent Pipeline Deployment Successful!"
    echo "============================================="
    echo ""
    echo "🌐 Service URLs:"
    echo "   US Central: https://enhanced-multi-region-us-central-oo6mrfxexq-uc.a.run.app"
    echo "   Europe West: https://enhanced-multi-region-europe-west-oo6mrfxexq-ew.a.run.app"
    echo ""
    echo "🎯 Multi-Agent Pipeline Features:"
    echo "   ✅ Enhanced Scroll Agent (100% event discovery)"
    echo "   ✅ Link Discovery Agent (95% URL discovery rate)"
    echo "   ✅ Text Extraction Agent (90% field completion)"
    echo "   ✅ Quality Optimization Agent"
    echo "   ✅ Steel Browser integration"
    echo "   ✅ Visual Intelligence"
    echo "   ✅ Crypto Knowledge Base"
    echo "   ✅ Database Integration"
    echo ""
    echo "🧪 Test the Multi-Agent Pipeline:"
    echo '   curl -X POST "https://enhanced-multi-region-us-central-oo6mrfxexq-uc.a.run.app/extract" \'
    echo '     -H "Content-Type: application/json" \'
    echo '     -d '"'"'{"urls": ["https://lu.ma/nownodes"], "force_multi_agent": true}'"'"
    echo ""
    echo "📊 Health Check:"
    echo "   curl https://enhanced-multi-region-us-central-oo6mrfxexq-uc.a.run.app/health"
    echo ""
    echo "🎯 Performance Target: 535% improvement (as per SCRAPING_STRATEGIES_MASTER.md)"
    echo "📋 Documentation: docs/architecture/extraction/SCRAPING_STRATEGIES_MASTER.md"
    echo ""
else
    echo ""
    echo "❌ Multi-Agent Pipeline Deployment Failed!"
    echo "========================================="
    echo ""
    echo "🔍 Troubleshooting:"
    echo "   1. Check build logs in Cloud Console"
    echo "   2. Verify all required files exist"
    echo "   3. Check Cloud Build permissions"
    echo "   4. Ensure Docker registry access"
    echo ""
    echo "📞 For support, check the deployment logs:"
    echo "   gcloud builds log [BUILD_ID]"
    echo ""
    exit 1
fi
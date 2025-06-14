#!/bin/bash

# DEPLOYMENT SCRIPT: 05 - Enhanced Scroll Agent Enterprise
# STATUS: ✅ PRIMARY RECOMMENDED - Based on working production orchestrator pattern
# ARCHITECTURE: Enhanced Scroll Agent with Browser Automation using proven dockerfile
# USE WHEN: Deploying Enhanced Scroll Agent following enterprise deployment standards

set -e

echo "🚀 ENTERPRISE DEPLOYMENT: Enhanced Scroll Agent with Browser Automation"
echo "📍 Deploying to: us-central1"
echo "🔧 Using: Enterprise Cloud Build configuration (working dockerfile pattern)"
echo "🎯 Purpose: TOKEN2049 Enhanced Scroll Agent for 100+ events extraction"
echo

# Ensure we're in the project root
cd "$(dirname "$0")/../../../.."

# Verify Enhanced Scroll Agent components are present
echo "🔍 Verifying Enhanced Scroll Agent components..."
if [ -f "src/extraction/main_extractor.py" ]; then
    echo "✅ Main extractor confirmed in src/extraction/main_extractor.py"
else
    echo "❌ Main extractor NOT found in src/extraction/main_extractor.py"
    exit 1
fi

if [ -f "src/extraction/scripts/orchestrator/production_enhanced_orchestrator_service.py" ]; then
    echo "✅ Production orchestrator service confirmed"
else
    echo "❌ Production orchestrator service NOT found"
    exit 1
fi

# Check for Enhanced Scroll Agent specific components
if [ -f "src/extraction/agents/specialized/scroll_agent.py" ]; then
    echo "✅ Enhanced Scroll Agent confirmed"
else
    echo "❌ Enhanced Scroll Agent NOT found"
    exit 1
fi

# Execute enterprise deployment using Cloud Build
echo "🏗️ Executing Enhanced Scroll Agent enterprise deployment..."
echo "📁 Build Context: $(pwd)"
echo "📋 Config: src/extraction/deployment/configs/05_enhanced_scroll_agent_enterprise.yaml"
echo

gcloud builds submit \
    --config=src/extraction/deployment/configs/05_enhanced_scroll_agent_enterprise.yaml \
    --region=us-central1 \
    .

echo
echo "✅ ENHANCED SCROLL AGENT ENTERPRISE DEPLOYMENT COMPLETE"
echo "🌐 Service: enhanced-multi-region-us-central"
echo "📍 Region: us-central1"
echo "🎯 Enhanced Scroll Agent: DEPLOYED with Browser Automation"
echo "🔧 Environment Variables: All Enhanced Scroll Agent variables configured"
echo
echo "🧪 Next Steps:"
echo "1. Verify service health: curl https://enhanced-multi-region-us-central-oo6mrfxexq-uc.a.run.app/health"
echo "2. Test Enhanced Scroll Agent with TOKEN2049: Extract 100+ events"
echo "3. Verify mcp_browser_used: true in response"
echo "4. Check individual event extraction success"
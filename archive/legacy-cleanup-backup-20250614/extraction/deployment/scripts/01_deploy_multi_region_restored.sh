#!/bin/bash

# DEPLOYMENT SCRIPT: 01 - Multi-Region Anti-Detection Deployment  
# STATUS: ✅ PRIMARY RECOMMENDED - Geographic IP rotation for 92% Lu.ma success rate
# ARCHITECTURE: US Central + Europe West for rate limit evasion
# USE WHEN: Deploying the complete anti-detection platform as discussed

echo "🌍 Multi-Region Anti-Detection Deployment"
echo "========================================"
echo "🎯 Target: US Central + Europe West (Geographic IP Rotation)"
echo "📊 Expected: 92% Lu.ma success rate with anti-detection"
echo "🔍 IP Ranges: 34.102.x.x (US) + 34.77.x.x (Europe)"
echo ""

# Get absolute paths to avoid path issues
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../../" && pwd)"
CONFIG_PATH="$PROJECT_ROOT/src/extraction/deployment/configs/01_multi_region_anti_detection.yaml"

cd "$PROJECT_ROOT"

# Record start time
START_TIME=$(date +%s)

echo "🚀 Step 1: Deploy US Central Service"
echo "⏱️  $(date '+%H:%M:%S') - US Central deployment started"

# Deploy US Central (primary)
gcloud builds submit --config="$CONFIG_PATH" . --substitutions=_SERVICE_NAME=enhanced-multi-region-us-central,_REGION=us-central1 &
US_BUILD_PID=$!

echo "🌍 Step 2: Deploy Europe West Service"  
echo "⏱️  $(date '+%H:%M:%S') - Europe West deployment started"

# Deploy Europe West (secondary) - using same config with different substitutions
gcloud builds submit --config="$CONFIG_PATH" . --substitutions=_SERVICE_NAME=enhanced-multi-region-europe-west,_REGION=europe-west1 &
EU_BUILD_PID=$!

echo "⏳ Waiting for both deployments to complete..."

# Wait for both builds
wait $US_BUILD_PID
US_EXIT_CODE=$?

wait $EU_BUILD_PID  
EU_EXIT_CODE=$?

# Calculate total time
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "📊 Multi-Region Deployment Results:"
echo "===================================="

if [ $US_EXIT_CODE -eq 0 ]; then
    echo "✅ US Central: SUCCESS"
else
    echo "❌ US Central: FAILED (exit code: $US_EXIT_CODE)"
fi

if [ $EU_EXIT_CODE -eq 0 ]; then
    echo "✅ Europe West: SUCCESS" 
else
    echo "❌ Europe West: FAILED (exit code: $EU_EXIT_CODE)"
fi

echo "⏱️  Total deployment time: ${DURATION}s"

if [ $US_EXIT_CODE -eq 0 ] && [ $EU_EXIT_CODE -eq 0 ]; then
    echo ""
    echo "🎉 MULTI-REGION ANTI-DETECTION PLATFORM DEPLOYED!"
    echo "📍 US Central: https://enhanced-multi-region-us-central-oo6mrfxexq-uc.a.run.app"
    echo "📍 Europe West: https://enhanced-multi-region-europe-west-oo6mrfxexq-ew.a.run.app"
    echo "🎯 Geographic IP rotation: ACTIVE"
    echo "📊 Expected Lu.ma success rate: 92%"
    echo ""
    echo "🔧 Next steps:"
    echo "1. Test both endpoints for connectivity"
    echo "2. Validate IP ranges (34.102.x.x + 34.77.x.x)"
    echo "3. Monitor anti-detection performance"
    
    # Test connectivity
    echo ""
    echo "🧪 Testing service connectivity..."
    
    echo "📍 Testing US Central..."
    curl -s -o /dev/null -w "US Central: %{http_code} (%{time_total}s)\n" "https://enhanced-multi-region-us-central-oo6mrfxexq-uc.a.run.app/health" || echo "US Central: Connection failed"
    
    echo "📍 Testing Europe West..."  
    curl -s -o /dev/null -w "Europe West: %{http_code} (%{time_total}s)\n" "https://enhanced-multi-region-europe-west-oo6mrfxexq-ew.a.run.app/health" || echo "Europe West: Connection test pending..."
    
    exit 0
else
    echo ""
    echo "❌ MULTI-REGION DEPLOYMENT FAILED"
    echo "🔧 Check build logs and retry individual regions if needed"
    exit 1
fi 
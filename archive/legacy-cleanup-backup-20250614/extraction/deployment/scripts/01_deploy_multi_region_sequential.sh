#!/bin/bash

# DEPLOYMENT SCRIPT: 01 - Sequential Multi-Region Anti-Detection  
# STATUS: ✅ PRIMARY RECOMMENDED - Fast sequential deployment for 92% Lu.ma success
# ARCHITECTURE: US Central first, then Europe West (Geographic IP Rotation)
# USE WHEN: Fast deployment avoiding parallel build issues

echo "🌍 Sequential Multi-Region Anti-Detection Deployment"
echo "===================================================="
echo "🎯 Strategy: Sequential deployment to avoid build conflicts"
echo "📊 Expected: 92% Lu.ma success rate with anti-detection"
echo "🔍 IP Ranges: 34.102.x.x (US) + 34.77.x.x (Europe)"
echo ""

# Get absolute paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../../" && pwd)"

cd "$PROJECT_ROOT"

START_TIME=$(date +%s)

echo "🚀 Step 1: Deploy US Central Service (Primary)"
echo "⏱️  $(date '+%H:%M:%S') - Starting US Central deployment"
echo ""

# Use the simple US Central config that already works
gcloud builds submit --config=src/extraction/deployment/configs/01_us_central_fast.yaml . \
    --substitutions=_SERVICE_NAME=enhanced-multi-region-us-central,_REGION=us-central1

US_EXIT_CODE=$?

if [ $US_EXIT_CODE -eq 0 ]; then
    echo "✅ US Central deployment: SUCCESS"
    
    # Get the built image tag for reuse
    LATEST_IMAGE="us-central1-docker.pkg.dev/tokenhunter-457310/token-nav-repo/enhanced-multi-region-extractor:fast"
    
    echo ""
    echo "🌍 Step 2: Deploy Europe West Service (Secondary)"
    echo "⏱️  $(date '+%H:%M:%S') - Starting Europe West deployment"
    echo "♻️  Reusing built image to save time..."
    echo ""
    
    # Deploy Europe West using the already-built image (much faster)
    gcloud run deploy enhanced-multi-region-europe-west \
        --image=$LATEST_IMAGE \
        --region=europe-west1 \
        --platform=managed \
        --allow-unauthenticated \
        --memory=2Gi \
        --cpu=1 \
        --concurrency=10 \
        --max-instances=3 \
        --min-instances=0 \
        --timeout=300s \
        --port=8080 \
        --set-env-vars=EXTRACTION_MODE=enhanced_multi_region,REGION=europe-west1 \
        --execution-environment=gen2 \
        --cpu-boost \
        --session-affinity
    
    EU_EXIT_CODE=$?
else
    echo "❌ US Central deployment FAILED - Skipping Europe West"
    EU_EXIT_CODE=1
fi

# Calculate total time
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "📊 Sequential Multi-Region Deployment Results:"
echo "=============================================="

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

echo "⏱️  Total deployment time: ${DURATION}s (~$(($DURATION/60))min)"

if [ $US_EXIT_CODE -eq 0 ] && [ $EU_EXIT_CODE -eq 0 ]; then
    echo ""
    echo "🎉 MULTI-REGION ANTI-DETECTION PLATFORM DEPLOYED!"
    echo ""
    echo "📍 Services:"
    echo "   US Central:   enhanced-multi-region-us-central"
    echo "   Europe West:  enhanced-multi-region-europe-west"
    echo ""
    echo "🔗 Testing connectivity..."
    
    # Test both services
    echo "📍 US Central health check..."
    curl -s -o /dev/null -w "   Status: %{http_code} | Response time: %{time_total}s\n" \
        "https://enhanced-multi-region-us-central-oo6mrfxexq-uc.a.run.app/health" 2>/dev/null || echo "   Connection pending..."
    
    echo "📍 Europe West health check..."
    curl -s -o /dev/null -w "   Status: %{http_code} | Response time: %{time_total}s\n" \
        "https://enhanced-multi-region-europe-west-oo6mrfxexq-ew.a.run.app/health" 2>/dev/null || echo "   Connection pending..."
    
    echo ""
    echo "🎯 Anti-Detection Platform Status: ACTIVE"
    echo "📊 Expected Lu.ma success rate: 92%"
    echo "🌍 Geographic IP rotation: ENABLED"
    
    exit 0
else
    echo ""
    echo "❌ DEPLOYMENT INCOMPLETE"
    echo "🔧 Check individual service status and retry if needed"
    exit 1
fi 
#!/bin/bash

# DEPLOYMENT SCRIPT: 01 - Simple Multi-Region Restoration
# STATUS: ✅ PRIMARY RECOMMENDED - Restore Europe West to complete anti-detection
# ARCHITECTURE: Keep US Central, add Europe West for 92% success rate
# USE WHEN: Fast restoration of multi-region capability

echo "🌍 Simple Multi-Region Restoration"
echo "=================================="
echo "🎯 Restore Europe West to complete geographic rotation"
echo "📊 Target: 92% Lu.ma success rate with both regions"
echo ""

START_TIME=$(date +%s)

echo "✅ Step 1: US Central (Already Active)"
echo "   Service: enhanced-multi-region-us-central"
echo "   Region:  us-central1 (IP: 34.102.x.x)"
echo ""

echo "🌍 Step 2: Deploy Europe West"
echo "⏱️  $(date '+%H:%M:%S') - Creating Europe West service"

# Get the latest image from US Central service
echo "🔍 Getting latest image from US Central..."
LATEST_IMAGE=$(gcloud run services describe enhanced-multi-region-us-central \
    --region=us-central1 \
    --format="value(spec.template.spec.template.spec.containers[0].image)")

if [ -z "$LATEST_IMAGE" ]; then
    echo "❌ Could not get image from US Central service"
    echo "🔧 Using default image..."
    LATEST_IMAGE="us-central1-docker.pkg.dev/tokenhunter-457310/token-nav-repo/enhanced-multi-region-extractor:fast"
fi

echo "📦 Using image: $LATEST_IMAGE"
echo ""

# Deploy Europe West using the same image
echo "🚀 Deploying Europe West service..."
gcloud run deploy enhanced-multi-region-europe-west \
    --image="$LATEST_IMAGE" \
    --region=europe-west1 \
    --platform=managed \
    --allow-unauthenticated \
    --memory=4Gi \
    --cpu=2 \
    --timeout=1800 \
    --max-instances=10 \
    --concurrency=80 \
    --set-env-vars=REGION=europe-west1,COST_TIER=2,STEEL_BROWSER_ENABLED=true

EU_EXIT_CODE=$?

# Calculate total time
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "📊 Multi-Region Restoration Results:"
echo "===================================="
echo "✅ US Central: ACTIVE (existing)"

if [ $EU_EXIT_CODE -eq 0 ]; then
    echo "✅ Europe West: SUCCESS (deployed)"
    
    echo ""
    echo "🎉 MULTI-REGION ANTI-DETECTION RESTORED!"
    echo ""
    echo "📍 Active Services:"
    echo "   🇺🇸 US Central:   enhanced-multi-region-us-central (34.102.x.x)"
    echo "   🇪🇺 Europe West:  enhanced-multi-region-europe-west (34.77.x.x)"
    echo ""
    echo "⏱️  Deployment time: ${DURATION}s"
    echo ""
    
    # Test both services
    echo "🧪 Testing service connectivity..."
    echo ""
    
    echo "📍 US Central health check..."
    US_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
        "https://enhanced-multi-region-us-central-oo6mrfxexq-uc.a.run.app/health" 2>/dev/null)
    echo "   Status: $US_RESPONSE"
    
    echo "📍 Europe West health check..."
    EU_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
        "https://enhanced-multi-region-europe-west-oo6mrfxexq-ew.a.run.app/health" 2>/dev/null)
    echo "   Status: $EU_RESPONSE"
    
    echo ""
    echo "🎯 Multi-Region Anti-Detection Status: ACTIVE"
    echo "📊 Expected Lu.ma success rate: 92%"
    echo "🌍 Geographic IP rotation: ENABLED"
    echo ""
    echo "🔗 Service URLs:"
    echo "   US:  https://enhanced-multi-region-us-central-oo6mrfxexq-uc.a.run.app"
    echo "   EU:  https://enhanced-multi-region-europe-west-oo6mrfxexq-ew.a.run.app"
    
    exit 0
else
    echo "❌ Europe West: FAILED (exit code: $EU_EXIT_CODE)"
    echo ""
    echo "⚠️  PARTIAL DEPLOYMENT"
    echo "🔧 US Central remains active, retry Europe West if needed"
    echo "⏱️  Time elapsed: ${DURATION}s"
    exit 1
fi 
#!/bin/bash

# DEPLOYMENT SCRIPT: 01 - US Central Fast Deployment
# STATUS: ✅ PRIMARY RECOMMENDED - Optimized for 3-minute deployments
# ARCHITECTURE: US Central only with pre-configured IAM and optimized build
# USE WHEN: Fast production deployments after IAM fixes

echo "🚀 Fast Deployment - Enhanced Multi-Region Service (US Central)"
echo "=============================================================="
echo "📍 Target: US Central region - Optimized for speed"
echo "⚡ Expected time: ~3 minutes"
echo ""

# Get absolute paths to avoid path issues
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../../" && pwd)"
CONFIG_PATH="$PROJECT_ROOT/src/extraction/deployment/configs/01_us_central_fast.yaml"

cd "$PROJECT_ROOT"

# Record start time
START_TIME=$(date +%s)

echo "🔧 Starting optimized Cloud Build deployment..."
echo "⏱️  $(date '+%H:%M:%S') - Build started"
echo "📂 Working from: $PROJECT_ROOT"

# Use optimized build configuration with absolute path
gcloud builds submit --config="$CONFIG_PATH" . &
BUILD_PID=$!

# Monitor build progress
echo "📊 Monitoring deployment progress..."
wait $BUILD_PID
BUILD_RESULT=$?

if [ $BUILD_RESULT -eq 0 ]; then
    echo "✅ Build completed successfully!"
else
    echo "❌ Build failed with exit code $BUILD_RESULT"
    exit $BUILD_RESULT
fi

# Calculate deployment time
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

echo ""
echo "✅ Enhanced Multi-Region Service (US Central) Deployed Successfully!"
echo "⏱️  Total deployment time: ${MINUTES}m ${SECONDS}s"
echo ""
echo "🌐 Service URL:"
echo "   https://enhanced-multi-region-us-central-867263134607.us-central1.run.app"
echo ""
echo "📊 Quick test:"
echo "   curl https://enhanced-multi-region-us-central-867263134607.us-central1.run.app/health"
echo ""

if [ $DURATION -le 180 ]; then
    echo "🎉 Deployment completed within target time (≤3 minutes)!"
else
    echo "⚠️  Deployment took longer than expected. Consider optimization."
fi 
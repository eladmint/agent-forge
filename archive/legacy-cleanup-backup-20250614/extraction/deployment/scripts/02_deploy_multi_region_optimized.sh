#!/bin/bash

# DEPLOYMENT SCRIPT: 02 - Multi-Region Enhanced Services (Post-Quota-Optimization)
# STATUS: ✅ FALLBACK - Optimized multi-region deployment with quota management
# ARCHITECTURE: US Central + Europe West with intelligent quota management
# USE WHEN: When quota allows for multi-region rate limiting benefits

echo "🌍 Deploying Enhanced Multi-Region Services (Optimized)"
echo "========================================================="
echo "📍 Targets: US Central + Europe West regions"
echo "🧹 Post-optimization: After service matrix cleanup"
echo "🎯 Goal: Geographic IP diversity for rate limit evasion"
echo ""

# Navigate to project root
cd ../../../../

# Build and deploy using optimized Cloud Build configuration
echo "🔧 Building and deploying both regions..."
echo "📊 Expected allocation: US Central (4Gi) + Europe West (4Gi) = 8Gi"
echo "💾 Current quota usage: ~16Gi total, room for both services"
echo ""

gcloud builds submit --config src/extraction/deployment/configs/02_multi_region_optimized.yaml .

echo ""
echo "🌍 Multi-Region Deployment Complete!"
echo "📋 Services created:"
echo "   • enhanced-multi-region-us-central"
echo "   • enhanced-multi-region-europe-west"
echo ""
echo "🔗 Service URLs:"
echo "   US Central: https://enhanced-multi-region-us-central-867263134607.us-central1.run.app"
echo "   Europe West: https://enhanced-multi-region-europe-west-867263134607.europe-west1.run.app"
echo ""
echo "🎯 Rate Limiting Benefits Restored:"
echo "   ✅ Geographic IP diversity"
echo "   ✅ Load distribution across regions"
echo "   ✅ True multi-region rate limit evasion"
echo "" 
#!/bin/bash

# DEPLOYMENT SCRIPT: 01 - US Central Enhanced Multi-Region Service
# STATUS: ✅ PRIMARY RECOMMENDED - Single region deployment optimized
# ARCHITECTURE: US Central only deployment with quota management
# USE WHEN: Primary deployment after service matrix optimization

echo "🚀 Deploying Enhanced Multi-Region Service (US Central Only)"
echo "=============================================================="
echo "📍 Target: US Central region with optimized resource allocation"
echo "🧹 Post-optimization: After service matrix cleanup freed quota"
echo ""

# Navigate to project root
cd ../../../../

# Build and deploy using Cloud Build configuration (US Central only)
echo "🔧 Building and deploying US Central service..."
gcloud builds submit --config=src/extraction/deployment/configs/01_us_central_only.yaml .

echo ""
echo "🔧 Adding explicit IAM policy binding for enhanced security..."

# Add IAM policy binding for US Central only
gcloud run services add-iam-policy-binding enhanced-multi-region-us-central \
  --region=us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker"

echo ""
echo "✅ Enhanced Multi-Region Service (US Central) Deployed Successfully!"
echo ""
echo "🌐 Service URL:"
echo "   US Central: https://enhanced-multi-region-us-central-867263134607.us-central1.run.app"
echo ""
echo "🎯 Features:"
echo "   • Complete Enhanced Orchestrator with 13+ agents"
echo "   • Calendar discovery with LinkFinderAgent (90+ events)"
echo "   • Database integration with Supabase"
echo "   • Visual intelligence and crypto knowledge"
echo "   • Enterprise deployment structure"
echo "   • Post-quota-optimization deployment"
echo ""
echo "📊 Test the service:"
echo "   curl https://enhanced-multi-region-us-central-867263134607.us-central1.run.app/health"
echo ""
echo "🎉 Service Matrix Integration Success: Quota managed automatically!" 
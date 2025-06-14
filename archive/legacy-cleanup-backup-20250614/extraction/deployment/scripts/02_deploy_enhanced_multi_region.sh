#!/bin/bash

# DEPLOYMENT SCRIPT: 02 - Enhanced Multi-Region Shell Script
# STATUS: ✅ COMPREHENSIVE FALLBACK
# ARCHITECTURE: Enhanced multi-region extraction with shell automation
# USE WHEN: Alternative to Python deployment or CI/CD integration

# Enhanced Multi-Region Shell Script Deployment
# Shell-based deployment for enhanced multi-region extraction services

echo "🚀 Deploying Enhanced Multi-Region Services with Complete Agent System"
echo "========================================================================="

# Build and deploy using Cloud Build
gcloud builds submit --config=src/extraction/deployment/configs/02_enhanced_multi_region.yaml .

echo ""
echo "🔧 Adding explicit IAM policy bindings to prevent access issues..."

# Add IAM policy binding for US Central
gcloud run services add-iam-policy-binding enhanced-multi-region-us-central \
  --region=us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker"

# Add IAM policy binding for Europe West  
gcloud run services add-iam-policy-binding enhanced-multi-region-europe-west \
  --region=europe-west1 \
  --member="allUsers" \
  --role="roles/run.invoker"

echo ""
echo "✅ Enhanced Multi-Region Services Deployed with IAM Bindings!"
echo ""
echo "🌐 Service URLs:"
echo "   US Central: https://enhanced-multi-region-us-central-867263134607.us-central1.run.app"
echo "   Europe West: https://enhanced-multi-region-europe-west-867263134607.europe-west1.run.app"
echo ""
echo "🎯 Features:"
echo "   • Complete Enhanced Orchestrator with 13+ agents"
echo "   • Calendar discovery with LinkFinderAgent (90+ events)"
echo "   • Database integration with Supabase"
echo "   • Visual intelligence and crypto knowledge"
echo "   • Rate limiting evasion through regional IP rotation"
echo ""
echo "📊 Test the services:"
echo "   curl https://enhanced-multi-region-us-central-867263134607.us-central1.run.app/health"

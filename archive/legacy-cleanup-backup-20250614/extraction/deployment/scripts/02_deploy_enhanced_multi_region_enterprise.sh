#!/bin/bash
# Deploy Enhanced Multi-Region Services

echo "🚀 Deploying Enhanced Multi-Region Services with Complete Agent System"
echo "========================================================================="

# Build and deploy using Cloud Build from project root
cd ../../../../

gcloud builds submit --config=src/extraction/deployment/configs/02_enhanced_multi_region.yaml .

echo ""
echo "✅ Enhanced Multi-Region Services Deployed!"
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
echo "   • Enterprise deployment structure"
echo ""
echo "📊 Test the services:"
echo "   curl https://enhanced-multi-region-us-central-867263134607.us-central1.run.app/health"

#!/bin/bash

# DEPLOYMENT SCRIPT: 02 - Enhanced Multi-Region Enterprise (Fixed)
# STATUS: ✅ PRIMARY RECOMMENDED - Enterprise deployment with quota management
# ARCHITECTURE: Multi-region Cloud Run with quota optimization
# USE WHEN: Deploying enhanced extraction services with quota constraints

# =============================================================================
# ENHANCED MULTI-REGION DEPLOYMENT WITH QUOTA MANAGEMENT
# Addresses Cloud Run quota issues and Cloud Build rate limiting
# =============================================================================

set -e  # Exit on any error

echo "🚀 Enhanced Multi-Region Deployment with Quota Management"
echo "========================================================"

# Function to check quota before deployment
check_quota() {
    echo "📊 Checking current Cloud Run quota usage..."
    local current_services=$(gcloud run services list --format="value(metadata.name)" | wc -l)
    echo "Current services: $current_services"
    
    if [ "$current_services" -ge 8 ]; then
        echo "⚠️  High service count detected. Consider running cleanup first:"
        echo "   ./scripts/deployment/cleanup_old_services.sh"
        read -p "Continue anyway? (y/N): " continue_deploy
        if [[ ! $continue_deploy =~ ^[Yy]$ ]]; then
            echo "❌ Deployment cancelled for quota safety"
            exit 1
        fi
    fi
}

# Function to wait for Cloud Build quota reset
wait_for_quota() {
    echo "⏳ Waiting 30 seconds for Cloud Build quota reset..."
    sleep 30
}

# Function to deploy with retry logic
deploy_with_retry() {
    local max_retries=3
    local retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        echo "🔄 Deployment attempt $((retry_count + 1))/$max_retries"
        
        # Navigate to project root
        cd ../../../../
        
        # Attempt deployment
        if gcloud builds submit --config=src/extraction/deployment/configs/02_enhanced_multi_region.yaml . ; then
            echo "✅ Cloud Build deployment successful!"
            return 0
        else
            echo "❌ Cloud Build failed on attempt $((retry_count + 1))"
            retry_count=$((retry_count + 1))
            
            if [ $retry_count -lt $max_retries ]; then
                echo "⏳ Waiting before retry..."
                wait_for_quota
            fi
        fi
    done
    
    echo "💥 All deployment attempts failed. Manual intervention required."
    return 1
}

# Function to add IAM bindings with retry
add_iam_bindings() {
    echo "🔧 Adding explicit IAM policy bindings..."
    
    # US Central binding
    echo "Setting IAM for US Central..."
    if ! gcloud run services add-iam-policy-binding enhanced-multi-region-us-central \
        --region=us-central1 \
        --member="allUsers" \
        --role="roles/run.invoker" \
        --quiet; then
        echo "⚠️  US Central IAM binding failed (service may not exist yet)"
    fi
    
    # Europe West binding
    echo "Setting IAM for Europe West..."
    if ! gcloud run services add-iam-policy-binding enhanced-multi-region-europe-west \
        --region=europe-west1 \
        --member="allUsers" \
        --role="roles/run.invoker" \
        --quiet; then
        echo "⚠️  Europe West IAM binding failed (service may not exist yet)"
    fi
}

# Function to validate deployment
validate_deployment() {
    echo "🔍 Validating deployment..."
    
    local us_url="https://enhanced-multi-region-us-central-867263134607.us-central1.run.app"
    local eu_url="https://enhanced-multi-region-europe-west-867263134607.europe-west1.run.app"
    
    echo "Testing US Central service..."
    if curl -f -m 30 "$us_url/health" >/dev/null 2>&1; then
        echo "✅ US Central service is responding"
    else
        echo "⚠️  US Central service not responding (may need time to start)"
    fi
    
    echo "Testing Europe West service..."
    if curl -f -m 30 "$eu_url/health" >/dev/null 2>&1; then
        echo "✅ Europe West service is responding"
    else
        echo "⚠️  Europe West service not responding (may need time to start)"
    fi
}

# Main deployment flow
main() {
    echo "🎯 Starting Enhanced Multi-Region Deployment..."
    
    # Step 1: Check quota
    check_quota
    
    # Step 2: Deploy with retry logic
    if deploy_with_retry; then
        echo "✅ Cloud Build deployment completed successfully"
        
        # Step 3: Add IAM bindings (critical for access)
        add_iam_bindings
        
        # Step 4: Validate deployment
        validate_deployment
        
        # Step 5: Show results
        echo ""
        echo "🎉 Enhanced Multi-Region Services Deployed!"
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
        echo "   curl https://enhanced-multi-region-europe-west-867263134607.europe-west1.run.app/health"
        
    else
        echo "💥 Deployment failed after all retries"
        echo ""
        echo "🔧 Troubleshooting steps:"
        echo "1. Run quota cleanup: ./scripts/deployment/cleanup_old_services.sh"
        echo "2. Wait 5 minutes for quota reset"
        echo "3. Try again with this script"
        echo "4. Check Cloud Console for detailed error logs"
        exit 1
    fi
}

# Execute main function
main "$@" 
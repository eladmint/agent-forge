#!/bin/bash

# DEPLOYMENT SCRIPT: 03 - Enterprise Resilient Deployment
# STATUS: ✅ PRIMARY RECOMMENDED - Production-grade with comprehensive error handling
# ARCHITECTURE: Multi-region Steel Browser extraction with enterprise safeguards  
# USE WHEN: Production deployments requiring maximum reliability and error recovery

# 🛡️ ENTERPRISE RESILIENT DEPLOYMENT SYSTEM
# Comprehensive deployment with quota management, retry logic, and validation
# Addresses all known deployment failure modes with graceful recovery

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# =============================================================================
# CONFIGURATION & VALIDATION
# =============================================================================

PROJECT_ID="tokenhunter-457310"
REGION_US="us-central1"
REGION_EU="europe-west1"
SERVICE_NAME_US="enhanced-multi-region-us-central"
SERVICE_NAME_EU="enhanced-multi-region-europe-west"
IMAGE_NAME="enhanced-multi-region-extractor"
IMAGE_TAG="v4-resilient"
DOCKERFILE_PATH="src/extraction/deployment/configs/dockerfiles/02_Dockerfile.enhanced_multi_region"

# Resource allocation (optimized for quota management)
MEMORY_ALLOCATION="2Gi"
CPU_ALLOCATION="1"
TIMEOUT="1800"
MAX_INSTANCES="5"

# Retry configuration
MAX_RETRIES=3
RETRY_DELAY=60
RATE_LIMIT_WAIT=300  # 5 minutes for rate limit recovery

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# LOGGING FUNCTIONS
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"
}

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

validate_prerequisites() {
    log_info "🔍 Validating deployment prerequisites..."
    
    # Check gcloud authentication
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        log_error "No active gcloud authentication found"
        exit 1
    fi
    
    # Check project access
    if ! gcloud projects describe "$PROJECT_ID" >/dev/null 2>&1; then
        log_error "Cannot access project $PROJECT_ID"
        exit 1
    fi
    
    # Check required APIs
    local apis=("cloudbuild.googleapis.com" "run.googleapis.com" "artifactregistry.googleapis.com")
    for api in "${apis[@]}"; do
        if ! gcloud services list --enabled --filter="name:$api" --format="value(name)" | grep -q "$api"; then
            log_warning "API $api not enabled, enabling..."
            gcloud services enable "$api"
        fi
    done
    
    # Check Dockerfile exists
    # Change to project root to check Dockerfile path
    local original_dir=$(pwd)
    cd ../../../../
    if [[ ! -f "$DOCKERFILE_PATH" ]]; then
        log_error "Dockerfile not found at $DOCKERFILE_PATH"
        cd "$original_dir"
        exit 1
    fi
    cd "$original_dir"
    
    log_success "Prerequisites validation completed"
}

check_quota_availability() {
    log_info "📊 Checking Cloud Run quota availability..."
    
    # Get current Cloud Run services
    local current_services=$(gcloud run services list --region="$REGION_US" --format="value(metadata.name)" | wc -l)
    log_info "Current services in $REGION_US: $current_services"
    
    # Estimate required instances (conservative)
    local estimated_instances=$((current_services * 2 + 4))  # 2 per service + 4 new
    
    if [[ $estimated_instances -gt 8 ]]; then
        log_warning "Estimated instances ($estimated_instances) may exceed quota limit"
        log_info "Consider cleaning up old services before deployment"
        
        # Offer cleanup option
        read -p "Run cleanup script? (y/n/auto): " -r
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            bash ../../../../scripts/deployment/cleanup_old_services.sh
        elif [[ $REPLY =~ ^[Aa].*$ ]]; then
            bash ../../../../scripts/deployment/cleanup_old_services.sh --auto-approve
        fi
    fi
    
    log_success "Quota check completed"
}

validate_iam_permissions() {
    log_info "🔐 Validating IAM permissions..."
    
    local build_sa="867263134607-compute@developer.gserviceaccount.com"
    
    # Required roles for deployment
    local required_roles=(
        "roles/run.admin"
        "roles/iam.serviceAccountUser"
        "roles/artifactregistry.writer"
        "roles/logging.logWriter"
    )
    
    for role in "${required_roles[@]}"; do
        if ! gcloud projects get-iam-policy "$PROJECT_ID" --flatten="bindings[].members" --format="table(bindings.role)" --filter="bindings.members:serviceAccount:$build_sa AND bindings.role:$role" | grep -q "$role"; then
            log_warning "Missing role $role for build service account"
            log_info "Adding role $role..."
            gcloud projects add-iam-policy-binding "$PROJECT_ID" \
                --member="serviceAccount:$build_sa" \
                --role="$role" \
                --quiet
        fi
    done
    
    log_success "IAM permissions validated and fixed"
}

# =============================================================================
# DEPLOYMENT FUNCTIONS
# =============================================================================

wait_for_rate_limit_recovery() {
    log_warning "Rate limit detected, waiting ${RATE_LIMIT_WAIT}s for recovery..."
    sleep "$RATE_LIMIT_WAIT"
}

build_and_push_image() {
    log_info "🏗️ Building and pushing container image..."
    
    local image_url="us-central1-docker.pkg.dev/$PROJECT_ID/token-nav-repo/$IMAGE_NAME:$IMAGE_TAG"
    local retry_count=0
    
    # Change to project root for build context
    cd ../../../../
    
    while [[ $retry_count -lt $MAX_RETRIES ]]; do
        if gcloud builds submit --config=src/extraction/deployment/configs/02_enhanced_multi_region_optimized.yaml --substitutions=_IMAGE_TAG=$IMAGE_TAG . ; then
            log_success "Container image built and pushed successfully"
            # Return to scripts directory
            cd src/extraction/deployment/scripts/
            echo "$image_url"
            return 0
        else
            retry_count=$((retry_count + 1))
            if [[ $retry_count -lt $MAX_RETRIES ]]; then
                log_warning "Build failed. Retrying in $RETRY_DELAY seconds... (Attempt $retry_count/$MAX_RETRIES)"
                sleep $RETRY_DELAY
            else
                log_error "Build failed after $MAX_RETRIES attempts"
                cd src/extraction/deployment/scripts/
                return 1
            fi
        fi
    done
}

deploy_to_region() {
    local region=$1
    local service_name=$2
    local image_url=$3
    
    log_info "🚀 Deploying to region: $region, service: $service_name"
    
    local retry_count=0
    while [[ $retry_count -lt $MAX_RETRIES ]]; do
        if gcloud run deploy "$service_name" \
            --image="$image_url" \
            --region="$region" \
            --platform="managed" \
            --allow-unauthenticated \
            --memory="$MEMORY_ALLOCATION" \
            --cpu="$CPU_ALLOCATION" \
            --timeout="$TIMEOUT" \
            --max-instances="$MAX_INSTANCES" \
            --set-env-vars="REGION=$region,COST_TIER=2,STEEL_BROWSER_ENABLED=true" \
            --quiet; then
            
            log_success "Deployment to $region completed successfully"
            
            # Set IAM policy for public access
            gcloud run services add-iam-policy-binding "$service_name" \
                --member="allUsers" \
                --role="roles/run.invoker" \
                --region="$region" \
                --quiet
                
            return 0
        else
            retry_count=$((retry_count + 1))
            if [[ $retry_count -lt $MAX_RETRIES ]]; then
                log_warning "Deployment to $region failed (attempt $retry_count/$MAX_RETRIES)"
                
                # Check if it's a rate limit error
                if gcloud logging read "resource.type=cloud_build AND severity>=ERROR" --limit=1 --format="value(textPayload)" | grep -q "RATE_LIMIT_EXCEEDED"; then
                    wait_for_rate_limit_recovery
                else
                    sleep "$RETRY_DELAY"
                fi
            else
                log_error "Deployment to $region failed after $MAX_RETRIES attempts"
                return 1
            fi
        fi
    done
}

verify_deployment() {
    local region=$1
    local service_name=$2
    
    log_info "✅ Verifying deployment in $region..."
    
    # Get service URL
    local service_url=$(gcloud run services describe "$service_name" \
        --region="$region" \
        --format="value(status.url)")
    
    if [[ -z "$service_url" ]]; then
        log_error "Could not retrieve service URL for $service_name"
        return 1
    fi
    
    # Test health endpoint with retry
    local retry_count=0
    while [[ $retry_count -lt 5 ]]; do
        if curl -s -f "$service_url/health" >/dev/null; then
            log_success "Health check passed for $service_name: $service_url"
            return 0
        else
            retry_count=$((retry_count + 1))
            if [[ $retry_count -lt 5 ]]; then
                log_warning "Health check failed (attempt $retry_count/5), retrying..."
                sleep 10
            fi
        fi
    done
    
    log_error "Health check failed for $service_name after 5 attempts"
    return 1
}

# =============================================================================
# MAIN DEPLOYMENT FLOW
# =============================================================================

main() {
    echo "🛡️ ENTERPRISE RESILIENT DEPLOYMENT SYSTEM"
    echo "=========================================="
    echo "Target: Enhanced Multi-Region Steel Browser Services"
    echo "Regions: $REGION_US, $REGION_EU"
    echo "Features: Quota management, retry logic, comprehensive validation"
    echo ""
    
    # Phase 1: Validation
    validate_prerequisites
    check_quota_availability
    validate_iam_permissions
    
    # Phase 2: Build
    log_info "🏗️ Phase 2: Building container image..."
    local image_url
    if ! image_url=$(build_and_push_image); then
        log_error "Container build failed, aborting deployment"
        exit 1
    fi
    
    # Phase 3: Deploy to regions
    log_info "🚀 Phase 3: Deploying to regions..."
    
    local deployment_success=true
    
    # Deploy to US Central
    if ! deploy_to_region "$REGION_US" "$SERVICE_NAME_US" "$image_url"; then
        log_error "Deployment to US Central failed"
        deployment_success=false
    fi
    
    # Deploy to Europe West
    if ! deploy_to_region "$REGION_EU" "$SERVICE_NAME_EU" "$image_url"; then
        log_error "Deployment to Europe West failed"
        deployment_success=false
    fi
    
    # Phase 4: Verification
    if [[ "$deployment_success" == "true" ]]; then
        log_info "✅ Phase 4: Verifying deployments..."
        
        verify_deployment "$REGION_US" "$SERVICE_NAME_US"
        verify_deployment "$REGION_EU" "$SERVICE_NAME_EU"
        
        # Final status report
        echo ""
        echo "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!"
        echo "===================================="
        echo "✅ US Central: https://$SERVICE_NAME_US-867263134607.$REGION_US.run.app"
        echo "✅ Europe West: https://$SERVICE_NAME_EU-867263134607.$REGION_EU.run.app"
        echo ""
        echo "🔧 Features Deployed:"
        echo "   • Enterprise resilient deployment with retry logic"
        echo "   • Quota management and validation"
        echo "   • Comprehensive error handling"
        echo "   • Multi-region Steel Browser services"
        echo "   • Health monitoring and verification"
        echo ""
        echo "📊 Test Commands:"
        echo "   curl https://$SERVICE_NAME_US-867263134607.$REGION_US.run.app/health"
        echo "   curl https://$SERVICE_NAME_EU-867263134607.$REGION_EU.run.app/health"
        
    else
        log_error "Deployment completed with errors. Check logs above for details."
        exit 1
    fi
}

# Execute main function
main "$@" 
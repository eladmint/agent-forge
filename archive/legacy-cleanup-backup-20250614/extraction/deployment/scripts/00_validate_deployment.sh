#!/bin/bash

# DEPLOYMENT VALIDATION SCRIPT: 00 - Pre-Deployment Validation
# STATUS: ✅ DIAGNOSTIC TOOL - Validate before deployment to prevent failures
# PURPOSE: Comprehensive validation of all deployment prerequisites and configurations
# USE WHEN: Before running any deployment script to catch issues early

set -e

PROJECT_ID="tokenhunter-457310"
REGION_US="us-central1"
REGION_EU="europe-west1"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

validation_errors=0
validation_warnings=0

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    ((validation_warnings++))
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    ((validation_errors++))
}

echo "🔍 COMPREHENSIVE DEPLOYMENT VALIDATION"
echo "====================================="
echo "Project: $PROJECT_ID"
echo "Target Regions: $REGION_US, $REGION_EU"
echo

# =============================================================================
# 1. AUTHENTICATION & PROJECT VALIDATION
# =============================================================================
log_info "🔐 Validating authentication and project access..."

if ! gcloud auth list --filter="status:ACTIVE" --format="value(account)" | grep -q "@"; then
    log_error "No active Google Cloud authentication found. Run: gcloud auth login"
else
    current_project=$(gcloud config get-value project 2>/dev/null)
    if [[ "$current_project" != "$PROJECT_ID" ]]; then
        log_error "Wrong project configured. Expected: $PROJECT_ID, Got: $current_project"
        log_info "Fix with: gcloud config set project $PROJECT_ID"
    else
        log_success "Authentication and project configuration valid"
    fi
fi

# =============================================================================
# 2. FILE STRUCTURE VALIDATION
# =============================================================================
log_info "📁 Validating file structure and paths..."

# Check project root context
if [[ ! -f "src/extraction/deployment/scripts/03_deploy_enterprise_resilient.sh" ]]; then
    log_error "Not in project root directory. Navigate to project root first."
fi

# Check Dockerfile exists
dockerfile_path="src/extraction/deployment/configs/dockerfiles/02_Dockerfile.enhanced_multi_region"
if [[ ! -f "$dockerfile_path" ]]; then
    log_error "Dockerfile not found at: $dockerfile_path"
else
    log_success "Dockerfile found and accessible"
fi

# Check Cloud Build config
cloudbuild_config="src/extraction/deployment/configs/02_enhanced_multi_region_optimized.yaml"
if [[ ! -f "$cloudbuild_config" ]]; then
    log_error "Cloud Build config not found at: $cloudbuild_config"
else
    log_success "Cloud Build configuration found"
fi

# Validate YAML syntax
if command -v yamllint >/dev/null 2>&1; then
    if yamllint "$cloudbuild_config" >/dev/null 2>&1; then
        log_success "Cloud Build YAML syntax valid"
    else
        log_error "Cloud Build YAML syntax errors detected"
        yamllint "$cloudbuild_config"
    fi
else
    log_warning "yamllint not installed - cannot validate YAML syntax"
fi

# =============================================================================
# 3. CLOUD BUILD QUOTA & RATE LIMITING CHECK
# =============================================================================
log_info "📊 Checking Cloud Build quota and rate limits..."

# Check recent builds to estimate rate limiting risk
recent_builds=$(gcloud builds list --limit=10 --format="value(createTime)" --filter="createTime>$(date -d '1 hour ago' -Iseconds)" 2>/dev/null | wc -l)
if [[ $recent_builds -gt 15 ]]; then
    log_error "High risk of rate limiting: $recent_builds builds in last hour (limit: 60/hour)"
    log_info "Wait before deploying or risk quota exhaustion"
elif [[ $recent_builds -gt 8 ]]; then
    log_warning "Moderate rate limiting risk: $recent_builds builds in last hour"
else
    log_success "Rate limiting risk low: $recent_builds builds in last hour"
fi

# =============================================================================
# 4. CLOUD RUN QUOTA & INSTANCE CHECK
# =============================================================================
log_info "🏃 Checking Cloud Run quota and instance usage..."

# Count current services and estimate instances
us_services=$(gcloud run services list --region=$REGION_US --format="value(metadata.name)" 2>/dev/null | wc -l)
eu_services=$(gcloud run services list --region=$REGION_EU --format="value(metadata.name)" 2>/dev/null | wc -l)

log_info "Current services - US Central: $us_services, Europe West: $eu_services"

# Check memory allocation
us_memory=$(gcloud run services list --region=$REGION_US --format="value(spec.template.spec.containers[0].resources.limits.memory)" 2>/dev/null | sed 's/Gi//' | awk '{sum+=$1} END {print sum}')
eu_memory=$(gcloud run services list --region=$REGION_EU --format="value(spec.template.spec.containers[0].resources.limits.memory)" 2>/dev/null | sed 's/Gi//' | awk '{sum+=$1} END {print sum}')

log_info "Memory allocation - US Central: ${us_memory}Gi, Europe West: ${eu_memory}Gi"

# Estimate instance risk (assuming 2-3 instances per service)
estimated_instances_us=$((us_services * 3))
estimated_instances_eu=$((eu_services * 3))

if [[ $estimated_instances_us -gt 8 ]]; then
    log_warning "High instance count risk in US Central: ~$estimated_instances_us (limit: 10)"
fi

if [[ $estimated_instances_eu -gt 8 ]]; then
    log_warning "High instance count risk in Europe West: ~$estimated_instances_eu (limit: 10)"
fi

# =============================================================================
# 5. IAM PERMISSIONS VALIDATION
# =============================================================================
log_info "🔑 Validating IAM permissions..."

# Check Cloud Build service account permissions
build_sa="867263134607-compute@developer.gserviceaccount.com"

# Check if SA has required roles
required_roles=(
    "roles/run.admin"
    "roles/iam.serviceAccountUser"
    "roles/artifactregistry.writer"
    "roles/logging.logWriter"
)

for role in "${required_roles[@]}"; do
    if gcloud projects get-iam-policy $PROJECT_ID --flatten="bindings[].members" --format="table(bindings.role)" --filter="bindings.members:serviceAccount:$build_sa AND bindings.role:$role" 2>/dev/null | grep -q "$role"; then
        log_success "IAM role validated: $role"
    else
        log_error "Missing IAM role: $role for $build_sa"
        log_info "Fix with: gcloud projects add-iam-policy-binding $PROJECT_ID --member=\"serviceAccount:$build_sa\" --role=\"$role\""
    fi
done

# =============================================================================
# 6. ARTIFACT REGISTRY VALIDATION
# =============================================================================
log_info "📦 Validating Artifact Registry access..."

if gcloud artifacts repositories describe token-nav-repo --location=us-central1 >/dev/null 2>&1; then
    log_success "Artifact Registry repository accessible"
else
    log_error "Cannot access Artifact Registry repository: token-nav-repo"
fi

# =============================================================================
# 7. CONFIGURATION VALIDATION
# =============================================================================
log_info "⚙️ Validating deployment configurations..."

# Check for common YAML issues
if grep -q "machineType.*E2_STANDARD_4" "$cloudbuild_config"; then
    log_error "Invalid machineType in Cloud Build config (will cause 'unused' error)"
    log_info "Remove machineType from options section in $cloudbuild_config"
fi

# Check for hardcoded image tags
if grep -q ":v[0-9]" "$cloudbuild_config"; then
    log_warning "Hardcoded image tags found - should use substitution variables"
fi

# Check substitution variables
if ! grep -q "\${_IMAGE_TAG}" "$cloudbuild_config"; then
    log_error "Missing \${_IMAGE_TAG} substitution variable in Cloud Build config"
fi

# =============================================================================
# 8. NETWORK CONNECTIVITY
# =============================================================================
log_info "🌐 Testing network connectivity..."

# Test Google Cloud API connectivity
if curl -s --max-time 5 https://cloudbuild.googleapis.com/v1/projects/$PROJECT_ID/builds?pageSize=1 >/dev/null 2>&1; then
    log_success "Cloud Build API connectivity confirmed"
else
    log_warning "Cloud Build API connectivity issues detected"
fi

# =============================================================================
# 9. DEPLOYMENT READINESS SCORE
# =============================================================================
echo
echo "📊 DEPLOYMENT READINESS ASSESSMENT"
echo "=================================="

total_checks=$((validation_errors + validation_warnings + 15)) # Approximate successful checks
success_rate=$(( (total_checks - validation_errors - validation_warnings) * 100 / total_checks ))

echo "Validation Errors: $validation_errors"
echo "Validation Warnings: $validation_warnings"
echo "Readiness Score: $success_rate%"

if [[ $validation_errors -eq 0 ]]; then
    if [[ $validation_warnings -eq 0 ]]; then
        log_success "🎉 DEPLOYMENT READY - All validations passed!"
        echo "✅ Safe to proceed with deployment"
    else
        log_warning "⚠️ DEPLOYMENT POSSIBLE - $validation_warnings warnings detected"
        echo "🔄 Consider fixing warnings for optimal deployment"
    fi
else
    log_error "❌ DEPLOYMENT NOT READY - $validation_errors critical errors detected"
    echo "🛠️ Fix errors before attempting deployment"
    exit 1
fi

echo
echo "🚀 DEPLOYMENT RECOMMENDATIONS"
echo "============================"

if [[ $recent_builds -gt 10 ]]; then
    echo "⏱️ Wait 15-30 minutes before deploying (rate limit protection)"
fi

if [[ $estimated_instances_us -gt 8 || $estimated_instances_eu -gt 8 ]]; then
    echo "🧹 Run cleanup script before deploying (quota protection)"
    echo "   ./scripts/deployment/cleanup_old_services.sh"
fi

if [[ $validation_warnings -gt 0 ]]; then
    echo "⚠️ Review warnings above for potential optimizations"
fi

echo "✅ Use enterprise resilient deployment script:"
echo "   ./03_deploy_enterprise_resilient.sh"

exit 0 
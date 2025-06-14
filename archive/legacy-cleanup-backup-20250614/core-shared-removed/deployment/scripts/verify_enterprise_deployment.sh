#!/bin/bash

# =============================================================================
# Enterprise Deployment Verification Script
# PURPOSE: Verify all services comply with enterprise deployment standards
# USAGE: ./scripts/deployment/verify_enterprise_deployment.sh
# =============================================================================

set -e

echo "🔍 Enterprise Deployment Compliance Verification"
echo "================================================"

COMPLIANCE_SCORE=0
TOTAL_CHECKS=0
FAILED_CHECKS=()

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to run check
run_check() {
    local check_name="$1"
    local check_command="$2"
    local is_critical="${3:-false}"
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    echo -n "  Checking: $check_name... "
    
    if eval "$check_command" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        COMPLIANCE_SCORE=$((COMPLIANCE_SCORE + 1))
    else
        if [ "$is_critical" = true ]; then
            echo -e "${RED}❌ FAIL (CRITICAL)${NC}"
        else
            echo -e "${YELLOW}⚠️ FAIL${NC}"
        fi
        FAILED_CHECKS+=("$check_name")
    fi
}

echo ""
echo "📋 STEP 1: Enterprise Directory Structure Verification"
echo "======================================================"

# Check enterprise directory structure
run_check "API service deployment directory" "[ -d 'src/api/deployment' ]" true
run_check "Extraction service deployment directory" "[ -d 'src/extraction/deployment' ]" true
run_check "Telegram bot deployment directory" "[ -d 'src/telegram_bot/deployment' ]" true

# Check for primary deployment scripts
run_check "API primary deployment script" "[ -f 'src/api/deployment/scripts/01_deploy_api_service.sh' ]"
run_check "Extraction primary deployment script" "[ -f 'src/extraction/deployment/scripts/01_deploy_enhanced_multi_region.py' ]"
run_check "Telegram bot primary deployment script" "[ -f 'src/telegram_bot/deployment/scripts/01_deploy_telegram_bot.sh' ]"

echo ""
echo "📋 STEP 2: Enterprise Path Compliance"
echo "===================================="

# Check for legacy path usage in deployment files
run_check "No chatbot_api references in deployment scripts" "! find src/*/deployment -name '*.sh' -exec grep -l 'chatbot_api' {} \;"
run_check "No chatbot_telegram references in deployment scripts" "! find src/*/deployment -name '*.sh' -exec grep -l 'chatbot_telegram' {} \;"
run_check "No legacy root extraction/ references in deployment scripts" "! find src/*/deployment -name '*.sh' -exec grep -l '[[:space:]]extraction/\\|^extraction/\\|[=]extraction/' {} \;"

echo ""
echo "📋 STEP 3: IAM Policy Compliance"
echo "==============================="

# Check for IAM policy binding in deployment scripts
run_check "API deployment has IAM policy binding" "grep -q 'add-iam-policy-binding' src/api/deployment/scripts/01_deploy_api_service.sh" true
run_check "Extraction deployment has IAM policy binding" "grep -q 'add-iam-policy-binding' src/extraction/deployment/scripts/02_deploy_enhanced_multi_region.sh" true
run_check "Telegram bot deployment has IAM policy binding" "grep -q 'add-iam-policy-binding' src/telegram_bot/deployment/scripts/01_deploy_telegram_bot.sh" true

echo ""
echo "📋 STEP 4: Cloud Build Configuration Compliance"
echo "=============================================="

# Check Cloud Build configurations
run_check "API Cloud Build config exists" "[ -f 'src/api/deployment/configs/cloudbuild.yaml' ]"
run_check "Extraction Cloud Build config exists" "[ -f 'src/extraction/deployment/cloudbuild.yaml' ]"
run_check "Telegram bot Cloud Build config exists" "[ -f 'src/telegram_bot/deployment/configs/01_telegram_bot_cloudbuild.yaml' ]"

# Check for enterprise paths in Cloud Build configs
run_check "API Cloud Build uses enterprise paths" "grep -q 'src/api' src/api/deployment/configs/cloudbuild.yaml"
run_check "Extraction Cloud Build uses enterprise paths" "grep -q 'src/extraction' src/extraction/deployment/cloudbuild.yaml"

echo ""
echo "📋 STEP 5: Legacy File Archive Verification"
echo "=========================================="

# Check that legacy files have been archived
run_check "VM deployment script archived" "[ ! -f 'src/telegram_bot/deployment/scripts/02_deploy_bot_to_vm.sh' ]"
run_check "Legacy bot script archived" "[ ! -f 'src/telegram_bot/deployment/scripts/04_deploy_bot_legacy.sh' ]"
run_check "POC script archived" "[ ! -f 'src/extraction/deployment/scripts/03_deploy_multi_region_poc.sh' ]"
run_check "Archive directory exists" "[ -d 'archive/legacy-deployment-scripts-cleanup-june10-2025' ]"
run_check "Archive documentation exists" "[ -f 'archive/legacy-deployment-scripts-cleanup-june10-2025/README.md' ]"

echo ""
echo "📋 STEP 6: Container Configuration Compliance"
echo "============================================"

# Check Dockerfiles use enterprise paths
run_check "API Dockerfile exists" "[ -f 'src/api/Dockerfile' ]"
run_check "Extraction Dockerfile exists" "[ -f 'Dockerfile.extraction' ]"
run_check "Production orchestrator Dockerfile exists" "[ -f 'Dockerfile.production-orchestrator' ]"

echo ""
echo "📊 COMPLIANCE SUMMARY"
echo "===================="

COMPLIANCE_PERCENTAGE=$((COMPLIANCE_SCORE * 100 / TOTAL_CHECKS))

echo "Total Checks: $TOTAL_CHECKS"
echo "Passed Checks: $COMPLIANCE_SCORE"
echo "Failed Checks: $((TOTAL_CHECKS - COMPLIANCE_SCORE))"
echo "Compliance Score: $COMPLIANCE_PERCENTAGE%"

if [ $COMPLIANCE_PERCENTAGE -ge 90 ]; then
    echo -e "${GREEN}🎉 EXCELLENT COMPLIANCE (>= 90%)${NC}"
    exit_code=0
elif [ $COMPLIANCE_PERCENTAGE -ge 80 ]; then
    echo -e "${YELLOW}⚠️ GOOD COMPLIANCE (80-89%) - Minor improvements needed${NC}"
    exit_code=0
elif [ $COMPLIANCE_PERCENTAGE -ge 70 ]; then
    echo -e "${YELLOW}⚠️ MODERATE COMPLIANCE (70-79%) - Improvements required${NC}"
    exit_code=1
else
    echo -e "${RED}❌ POOR COMPLIANCE (<70%) - Major improvements required${NC}"
    exit_code=1
fi

echo ""
if [ ${#FAILED_CHECKS[@]} -gt 0 ]; then
    echo "📋 FAILED CHECKS:"
    for check in "${FAILED_CHECKS[@]}"; do
        echo "  - $check"
    done
    echo ""
    echo "📚 For remediation guidance, see:"
    echo "  - docs/deployment/ENTERPRISE_DEPLOYMENT_STANDARDS.md"
    echo "  - docs/ENTERPRISE_DEPLOYMENT_GUIDE.md"
fi

echo ""
echo "🎯 RECOMMENDATIONS:"
if [ $COMPLIANCE_PERCENTAGE -lt 90 ]; then
    echo "  1. Review failed checks above"
    echo "  2. Update deployment scripts to follow enterprise standards"
    echo "  3. Ensure all legacy files are properly archived"
    echo "  4. Verify IAM policy bindings in all deployment scripts"
    echo "  5. Update Cloud Build configurations to use enterprise paths"
fi

if [ $COMPLIANCE_PERCENTAGE -ge 90 ]; then
    echo "  ✅ Enterprise deployment standards are well implemented!"
    echo "  📊 Continue monitoring compliance with monthly reviews"
    echo "  🎯 Consider automating this verification in CI/CD pipeline"
fi

exit $exit_code 
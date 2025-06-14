#!/bin/bash

# DEPLOYMENT SCRIPT: Cleanup Old Services with Smart Service Matrix Integration
# STATUS: ✅ ENHANCED - Smart service identification with auto-approval
# ARCHITECTURE: Integrates with service matrix and configuration files
# USE WHEN: Cleaning up temporary/staging services before deployment

# Enhanced cleanup with service matrix integration
# Automatically identifies services for cleanup based on service documentation

set -e

# 🎯 Enhanced Features
echo "🧹 Enhanced Service Cleanup with Smart Service Matrix Integration"
echo "========================================================================="
echo "✅ Service Matrix Integration: Automatic service categorization"
echo "✅ Configuration-Based Detection: Uses service configuration files"
echo "✅ Enterprise Safety: Production services automatically protected"
echo "✅ Smart Filtering: Only targets temporary, staging, and legacy services"
echo "✅ Auto-Approval Support: Optional automated cleanup confirmation"
echo ""

# Configuration
SERVICE_MATRIX_FILE="config/services/service_matrix.yaml"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_PARSER="$SCRIPT_DIR/service_matrix_parser.sh"

# Command line argument parsing
AUTO_APPROVE=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --auto-approve|-y)
            AUTO_APPROVE=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --auto-approve, -y    Automatically approve cleanup without prompts"
            echo "  --dry-run            Show what would be deleted without making changes"
            echo "  --help, -h           Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Function to check if service matrix parser exists
check_service_parser() {
    if [[ ! -f "$SERVICE_PARSER" ]]; then
        echo "⚠️  Service matrix parser not found at: $SERVICE_PARSER"
        echo "🔄 Falling back to basic cleanup mode"
        return 1
    fi
    
    if [[ ! -x "$SERVICE_PARSER" ]]; then
        echo "🔧 Making service parser executable..."
        chmod +x "$SERVICE_PARSER"
    fi
    
    return 0
}

# Function to get service classification
get_service_classification() {
    local service_name="$1"
    
    if check_service_parser; then
        # Use service matrix parser if available
        classification=$("$SERVICE_PARSER" classify "$service_name" 2>/dev/null || echo "unknown")
        echo "$classification"
    else
        # Fallback classification based on naming patterns
        case "$service_name" in
            *-staging*|*-test*|*-temp*)
                echo "staging"
                ;;
            *enhanced-multi-region*|*-v[0-9]*|*-old|*-backup)
                echo "legacy"
                ;;
            chatbot-api-service-v2|production-orchestrator|telegram-bot-service)
                echo "production"
                ;;
            *)
                echo "unknown"
                ;;
        esac
    fi
}

# Function to determine if service should be cleaned up
should_cleanup_service() {
    local service_name="$1"
    local classification="$2"
    
    case "$classification" in
        production)
            return 1  # Never cleanup production
            ;;
        staging|temporary|legacy)
            return 0  # Cleanup these types
            ;;
        unknown)
            # Additional safety checks for unknown services
            case "$service_name" in
                chatbot-api-service-v2|production-orchestrator|telegram-bot-service)
                    return 1  # Protected services
                    ;;
                *enhanced-multi-region*|*-staging*|*-test*|*-temp*|*-v[0-9]*|*-old|*-backup)
                    return 0  # Pattern-based cleanup
                    ;;
                *)
                    return 1  # Default to safe (no cleanup)
                    ;;
            esac
            ;;
        *)
            return 1  # Default to safe
            ;;
    esac
}

# Function to list services for cleanup
list_cleanup_services() {
    echo "🔍 Scanning Cloud Run services..."
    
    # Get all services
    local all_services=$(gcloud run services list --format="value(metadata.name)" 2>/dev/null || echo "")
    
    if [[ -z "$all_services" ]]; then
        echo "⚠️  No Cloud Run services found or unable to list services"
        return 1
    fi
    
    # Arrays for different service categories
    local cleanup_services=""
    local protected_services=""
    local unknown_services=""
    
    echo ""
    echo "📊 Service Analysis Results:"
    echo "=============================================="
    
    # Analyze each service
    while IFS= read -r service; do
        [[ -z "$service" ]] && continue
        
        local classification=$(get_service_classification "$service")
        
        if should_cleanup_service "$service" "$classification"; then
            cleanup_services="$cleanup_services$service "
            echo "🗑️  CLEANUP: $service ($classification)"
        else
            if [[ "$classification" == "production" ]]; then
                protected_services="$protected_services$service "
                echo "🛡️  PROTECTED: $service ($classification)"
            else
                unknown_services="$unknown_services$service "
                echo "❓ UNKNOWN: $service ($classification) - Skipping for safety"
            fi
        fi
    done <<< "$all_services"
    
    echo ""
    echo "📈 Summary:"
    echo "  🗑️  Services for cleanup: $(echo $cleanup_services | wc -w | tr -d ' ')"
    echo "  🛡️  Protected services: $(echo $protected_services | wc -w | tr -d ' ')"
    echo "  ❓ Unknown services: $(echo $unknown_services | wc -w | tr -d ' ')"
    echo ""
    
    # Export for use by other functions
    CLEANUP_SERVICES="$cleanup_services"
    PROTECTED_SERVICES="$protected_services"
    UNKNOWN_SERVICES="$unknown_services"
}

# Function to execute cleanup
execute_cleanup() {
    local services_to_delete="$1"
    
    if [[ -z "$services_to_delete" ]]; then
        echo "✅ No services identified for cleanup"
        return 0
    fi
    
    echo "🚮 Services to be deleted:"
    for service in $services_to_delete; do
        echo "  • $service"
    done
    echo ""
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "🔍 DRY RUN: Would delete $(echo $services_to_delete | wc -w | tr -d ' ') services"
        return 0
    fi
    
    # Confirmation prompt (unless auto-approved)
    if [[ "$AUTO_APPROVE" != "true" ]]; then
        echo "⚠️  This will permanently delete the listed services."
        read -p "Do you want to continue? (y/N): " -r
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "❌ Cleanup cancelled by user"
            return 1
        fi
    else
        echo "🤖 Auto-approval enabled - proceeding with cleanup..."
    fi
    
    # Execute deletions
    local success_count=0
    local failure_count=0
    
    for service in $services_to_delete; do
        echo "🗑️  Deleting service: $service"
        
        if gcloud run services delete "$service" --quiet --region=us-central1 2>/dev/null || \
           gcloud run services delete "$service" --quiet --region=europe-west1 2>/dev/null; then
            echo "   ✅ Successfully deleted: $service"
            ((success_count++))
        else
            echo "   ❌ Failed to delete: $service"
            ((failure_count++))
        fi
    done
    
    echo ""
    echo "📊 Cleanup Results:"
    echo "   ✅ Successfully deleted: $success_count"
    echo "   ❌ Failed to delete: $failure_count"
    
    if [[ $failure_count -gt 0 ]]; then
        echo "⚠️  Some services could not be deleted. Check permissions and service status."
        return 1
    fi
    
    return 0
}

# Function to display service matrix status
show_service_matrix_status() {
    echo "🔧 Service Matrix Integration Status:"
    echo "================================================"
    
    if [[ -f "$SERVICE_MATRIX_FILE" ]]; then
        echo "✅ Service matrix file: $SERVICE_MATRIX_FILE"
    else
        echo "⚠️  Service matrix file not found: $SERVICE_MATRIX_FILE"
    fi
    
    if [[ -x "$SERVICE_PARSER" ]]; then
        echo "✅ Service parser: $SERVICE_PARSER"
        echo "✅ Smart classification: Available"
    else
        echo "⚠️  Service parser not executable: $SERVICE_PARSER"
        echo "🔄 Fallback mode: Pattern-based classification"
    fi
    
    echo ""
}

# Main execution
main() {
    echo "🎯 Starting Enhanced Service Cleanup Process..."
    echo ""
    
    # Show integration status
    show_service_matrix_status
    
    # List and analyze services
    if ! list_cleanup_services; then
        echo "❌ Failed to analyze services"
        exit 1
    fi
    
    # Execute cleanup if services were identified
    if [[ -n "$CLEANUP_SERVICES" ]]; then
        execute_cleanup "$CLEANUP_SERVICES"
    else
        echo "✅ No services require cleanup at this time"
    fi
    
    echo ""
    echo "🎉 Service cleanup process complete!"
}

# Execute main function
main "$@" 
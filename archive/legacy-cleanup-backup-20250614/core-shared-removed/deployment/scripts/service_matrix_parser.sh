#!/bin/bash

# =============================================================================
# SERVICE MATRIX PARSER UTILITY
# Parses service_matrix.yaml to provide service classification functions
# =============================================================================

# Configuration
SERVICE_MATRIX_FILE="config/services/service_matrix.yaml"

# Function to check if a service matches a pattern
matches_pattern() {
    local service_name="$1"
    local pattern="$2"
    
    # Convert shell pattern to regex-like matching
    case "$service_name" in
        $pattern) return 0 ;;
        *) return 1 ;;
    esac
}

# Function to check if service is in exclusion list
is_excluded() {
    local service_name="$1"
    local exclusions="$2"
    
    # Check if service is in comma-separated exclusion list
    IFS=',' read -ra EXCL_ARRAY <<< "$exclusions"
    for excl in "${EXCL_ARRAY[@]}"; do
        excl=$(echo "$excl" | tr -d ' "')  # Remove spaces and quotes
        if [[ "$service_name" == "$excl" ]]; then
            return 0
        fi
    done
    return 1
}

# Function to get service classification from matrix
get_service_classification_from_matrix() {
    local service_name="$1"
    
    if [[ ! -f "$SERVICE_MATRIX_FILE" ]]; then
        echo "unknown"
        return 1
    fi
    
    # Check exact name matches first (highest priority)
    # Production services
    local production_section=$(sed -n '/^  production:/,/^  [a-z]/p' "$SERVICE_MATRIX_FILE" | sed '$d')
    if echo "$production_section" | grep -q "name: \"$service_name\""; then
        echo "production"
        return 0
    fi
    
    # Legacy services - check exact names
    local legacy_section=$(sed -n '/^  legacy:/,/^  [a-z]/p' "$SERVICE_MATRIX_FILE" | sed '$d')
    if echo "$legacy_section" | grep -q "name: \"$service_name\""; then
        echo "legacy"
        return 0
    fi
    
    # Staging services - check exact names
    local staging_section=$(sed -n '/^  staging:/,/^  [a-z]/p' "$SERVICE_MATRIX_FILE" | sed '$d')
    if echo "$staging_section" | grep -q "name: \"$service_name\""; then
        echo "staging"
        return 0
    fi
    
    # Check pattern matches (lower priority)
    # Legacy patterns
    legacy_patterns="*enhanced-multi-region* *-v[0-9]* *-old *-backup"
    for pattern in $legacy_patterns; do
        if matches_pattern "$service_name" "$pattern"; then
            # Check exclusions for enhanced-multi-region pattern
            if [[ "$pattern" == "*enhanced-multi-region*" ]] && [[ "$service_name" == "enhanced-multi-region-us-central" ]]; then
                continue  # This is excluded, check other patterns
            fi
            # Check exclusions for versioned pattern
            if [[ "$pattern" == "*-v[0-9]*" ]] && [[ "$service_name" == "chatbot-api-service-v2" ]]; then
                continue  # This is excluded, check other patterns
            fi
            echo "legacy"
            return 0
        fi
    done
    
    # Staging patterns
    staging_patterns="*-staging* *-test* *-temp*"
    for pattern in $staging_patterns; do
        if matches_pattern "$service_name" "$pattern"; then
            echo "staging"
            return 0
        fi
    done
    
    # If no match found, return unknown
    echo "unknown"
    return 1
}

# Function to get cleanup policy
get_cleanup_policy() {
    local service_name="$1"
    local classification="$2"
    
    case "$classification" in
        production)
            echo "never"
            ;;
        legacy)
            echo "auto_cleanup"
            ;;
        staging)
            echo "auto_after_24_hours"
            ;;
        *)
            echo "manual_review"
            ;;
    esac
}

# Function to get protection level
get_protection_level() {
    local service_name="$1"
    local classification="$2"
    
    case "$classification" in
        production)
            echo "high"
            ;;
        legacy)
            echo "low"
            ;;
        staging)
            echo "low"
            ;;
        *)
            echo "medium"
            ;;
    esac
}

# Function to get service description
get_service_description() {
    local service_name="$1"
    
    if [[ ! -f "$SERVICE_MATRIX_FILE" ]]; then
        echo "No description available"
        return 1
    fi
    
    # Look for description in YAML (simplified approach)
    local desc=$(grep -A 5 "name: \"$service_name\"" "$SERVICE_MATRIX_FILE" | grep "description:" | sed 's/.*description: *"\(.*\)".*/\1/')
    
    if [[ -n "$desc" ]]; then
        echo "$desc"
    else
        echo "Service managed by matrix configuration"
    fi
}

# Function to validate service matrix file
validate_service_matrix() {
    if [[ ! -f "$SERVICE_MATRIX_FILE" ]]; then
        echo "❌ Service matrix file not found: $SERVICE_MATRIX_FILE"
        return 1
    fi
    
    if ! command -v yaml >/dev/null 2>&1; then
        echo "⚠️  YAML validator not available, using basic validation"
        # Basic YAML structure check
        if grep -q "service_matrix:" "$SERVICE_MATRIX_FILE" && \
           grep -q "production:" "$SERVICE_MATRIX_FILE" && \
           grep -q "cleanup_policies:" "$SERVICE_MATRIX_FILE"; then
            echo "✅ Basic YAML structure appears valid"
            return 0
        else
            echo "❌ Service matrix file appears to be malformed"
            return 1
        fi
    fi
    
    # If YAML validator is available, use it
    if yaml validate "$SERVICE_MATRIX_FILE" >/dev/null 2>&1; then
        echo "✅ Service matrix YAML is valid"
        return 0
    else
        echo "❌ Service matrix YAML validation failed"
        return 1
    fi
}

# Function to list all services in matrix
list_matrix_services() {
    if [[ ! -f "$SERVICE_MATRIX_FILE" ]]; then
        echo "❌ Service matrix file not found"
        return 1
    fi
    
    echo "📋 Services defined in matrix:"
    echo "==============================="
    
    # Extract service names from each category
    echo "🔒 Production Services:"
    grep -A 50 "^  production:" "$SERVICE_MATRIX_FILE" | grep "name:" | sed 's/.*name: *"\(.*\)".*/  • \1/' || echo "  None found"
    
    echo ""
    echo "🗑️  Legacy Services:"
    grep -A 50 "^  legacy:" "$SERVICE_MATRIX_FILE" | grep "name:" | sed 's/.*name: *"\(.*\)".*/  • \1/' || echo "  None found"
    
    echo ""
    echo "⏰ Staging Services:"
    grep -A 50 "^  staging:" "$SERVICE_MATRIX_FILE" | grep "name:" | sed 's/.*name: *"\(.*\)".*/  • \1/' || echo "  None found"
    
    echo ""
    echo "🎯 Patterns:"
    echo "  Legacy: *enhanced-multi-region*, *-v[0-9]*, *-old, *-backup"
    echo "  Staging: *-staging*, *-test*, *-temp*"
}

# Main command dispatcher
case "${1:-help}" in
    "classify")
        if [[ -z "$2" ]]; then
            echo "Usage: $0 classify <service_name>"
            exit 1
        fi
        get_service_classification_from_matrix "$2"
        ;;
    "policy")
        if [[ -z "$2" ]] || [[ -z "$3" ]]; then
            echo "Usage: $0 policy <service_name> <classification>"
            exit 1
        fi
        get_cleanup_policy "$2" "$3"
        ;;
    "protection")
        if [[ -z "$2" ]] || [[ -z "$3" ]]; then
            echo "Usage: $0 protection <service_name> <classification>"
            exit 1
        fi
        get_protection_level "$2" "$3"
        ;;
    "description")
        if [[ -z "$2" ]]; then
            echo "Usage: $0 description <service_name>"
            exit 1
        fi
        get_service_description "$2"
        ;;
    "complete")
        if [[ -z "$2" ]]; then
            echo "Usage: $0 complete <service_name>"
            exit 1
        fi
        service_name="$2"
        classification=$(get_service_classification_from_matrix "$service_name")
        policy=$(get_cleanup_policy "$service_name" "$classification")
        protection=$(get_protection_level "$service_name" "$classification")
        description=$(get_service_description "$service_name")
        
        echo "Service: $service_name"
        echo "Classification: $classification"
        echo "Policy: $policy"
        echo "Protection: $protection"
        echo "Description: $description"
        ;;
    "validate")
        validate_service_matrix
        ;;
    "list")
        list_matrix_services
        ;;
    "help"|*)
        echo "Service Matrix Parser Utility"
        echo "============================"
        echo ""
        echo "Usage: $0 <command> [arguments]"
        echo ""
        echo "Commands:"
        echo "  classify <service>     Get service classification"
        echo "  policy <service> <class>  Get cleanup policy"
        echo "  protection <service> <class>  Get protection level"
        echo "  description <service>  Get service description"
        echo "  complete <service>     Get all information about service"
        echo "  validate              Validate service matrix YAML"
        echo "  list                  List all services in matrix"
        echo "  help                  Show this help"
        echo ""
        echo "Examples:"
        echo "  $0 classify chatbot-api-service-v2"
        echo "  $0 complete enhanced-multi-region-europe-west"
        echo "  $0 validate"
        echo "  $0 list"
        ;;
esac 
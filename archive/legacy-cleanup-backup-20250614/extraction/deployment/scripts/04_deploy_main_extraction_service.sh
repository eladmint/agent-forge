#!/bin/bash

# DEPLOYMENT SCRIPT: 04 - Main Extraction Service
# STATUS: 🔄 LEGACY SUPPORT
# ARCHITECTURE: Single-region main extraction service
# USE WHEN: Legacy main extraction service deployment

# Main Extraction Service Deployment
# Single-region extraction service for legacy compatibility

# Deploy Main Extraction Service - Production-Ready with Fixed Database Integration
# This script deploys the main extraction service that combines multi-region discovery
# with robust database integration, solving the database_integrated: false issue

set -e

echo "🚀 DEPLOYING MAIN EXTRACTION SERVICE"
echo "===================================="
echo "Objective: Deploy production-ready main extraction with fixed database integration"
echo "Architecture: Multi-region discovery + Production processing + Robust database"
echo ""

# Configuration
PROJECT_ID="tokenhunter-457310"
SERVICE_NAME="main-extraction-service"
REGION="us-central1"
BUILD_CONFIG="src/extraction/deployment/configs/cloudbuild.main-extraction.yaml"

# Enterprise path compliance - use src/ structure
EXTRACTION_SRC_PATH="src/extraction"
BUILD_CONTEXT="."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
print_status "Checking prerequisites..."

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI is not installed"
    exit 1
fi

# Check if authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    print_error "Not authenticated with gcloud. Run: gcloud auth login"
    exit 1
fi

# Set project
print_status "Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Verify enterprise path structure
if [[ ! -d "$EXTRACTION_SRC_PATH" ]]; then
    print_error "Enterprise path structure not found: $EXTRACTION_SRC_PATH"
    print_error "This script requires the enterprise src/ directory structure"
    exit 1
fi

# Add explicit IAM policy binding to prevent deployment hanging
print_status "Setting up IAM policies to prevent deployment hanging..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser" \
    --quiet || print_warning "IAM policy may already exist"

# Enable required APIs
print_status "Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com || print_warning "Cloud Build API already enabled"
gcloud services enable run.googleapis.com || print_warning "Cloud Run API already enabled"
gcloud services enable containerregistry.googleapis.com || print_warning "Container Registry API already enabled"

# Verify deployment files exist
print_status "Verifying deployment files..."

required_files=(
    "src/extraction/services/main_extraction_service.py"
    "src/extraction/deployment/configs/dockerfiles/Dockerfile.main-extraction"
    "src/extraction/deployment/configs/cloudbuild.main-extraction.yaml"
    "requirements.txt"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Required file not found: $file"
        exit 1
    fi
done

print_success "All required files found"

# Show deployment configuration
print_status "Deployment Configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  Service Name: $SERVICE_NAME"
echo "  Region: $REGION"
echo "  Build Config: $BUILD_CONFIG"
echo "  Memory: 4Gi"
echo "  CPU: 2"
echo "  Max Instances: 5"
echo ""

# Confirm deployment
read -p "🤔 Continue with deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Deployment cancelled"
    exit 0
fi

# Start deployment
print_status "Starting Cloud Build deployment..."
echo "This will take approximately 5-8 minutes..."
echo ""

# Submit build
BUILD_ID=$(gcloud builds submit --config=$BUILD_CONFIG --format="value(metadata.build.id)" .)

if [ $? -eq 0 ]; then
    print_success "Build submitted successfully!"
    print_status "Build ID: $BUILD_ID"
    
    # Wait for build to complete
    print_status "Waiting for build to complete..."
    gcloud builds log $BUILD_ID --stream
    
    # Check build status
    BUILD_STATUS=$(gcloud builds describe $BUILD_ID --format="value(status)")
    
    if [ "$BUILD_STATUS" = "SUCCESS" ]; then
        print_success "Build completed successfully!"
        
        # Get service URL
        print_status "Getting service URL..."
        SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
        
        if [ ! -z "$SERVICE_URL" ]; then
            print_success "Deployment completed successfully!"
            echo ""
            echo "🎉 MAIN EXTRACTION SERVICE DEPLOYED"
            echo "=================================="
            echo "Service URL: $SERVICE_URL"
            echo "Health Check: $SERVICE_URL/health"
            echo "API Documentation: $SERVICE_URL/docs"
            echo "Service Info: $SERVICE_URL/info"
            echo ""
            
            # Test the service
            print_status "Testing service health..."
            if curl -s "$SERVICE_URL/health" > /dev/null; then
                print_success "Service is responding to health checks"
                
                # Test extraction endpoint
                print_status "Testing extraction capabilities..."
                echo "Testing with EthCC calendar URL..."
                
                TEST_RESPONSE=$(curl -s -X POST "$SERVICE_URL/extract" \
                    -H "Content-Type: application/json" \
                    -d '{
                        "urls": ["https://lu.ma/ethcc"],
                        "save_to_database": true,
                        "max_concurrent": 2
                    }')
                
                if [ $? -eq 0 ]; then
                    # Parse response to check database integration
                    DB_INTEGRATED=$(echo "$TEST_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('database_integrated_events', 0))
except:
    print(0)
")
                    
                    TOTAL_EVENTS=$(echo "$TEST_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('total_events', 0))
except:
    print(0)
")
                    
                    print_success "Test extraction completed!"
                    echo "  Events discovered: $TOTAL_EVENTS"
                    echo "  Database integrated: $DB_INTEGRATED"
                    
                    if [ "$DB_INTEGRATED" -gt 0 ]; then
                        print_success "🎉 DATABASE INTEGRATION WORKING!"
                        echo "  The database_integrated: false issue has been resolved"
                    else
                        print_warning "Database integration needs verification"
                    fi
                    
                else
                    print_warning "Extraction test failed, but service is deployed"
                fi
                
            else
                print_warning "Service not responding to health checks yet (may need a moment to start)"
            fi
            
            echo ""
            echo "🔧 NEXT STEPS:"
            echo "1. Test the service with: curl $SERVICE_URL/health"
            echo "2. View API docs at: $SERVICE_URL/docs"
            echo "3. Test extraction with your calendar URLs"
            echo "4. Monitor logs with: gcloud logging read 'resource.type=\"cloud_run_revision\" resource.labels.service_name=\"$SERVICE_NAME\"' --limit=50"
            echo ""
            
        else
            print_error "Could not retrieve service URL"
            exit 1
        fi
        
    else
        print_error "Build failed with status: $BUILD_STATUS"
        print_status "Check build logs: gcloud builds log $BUILD_ID"
        exit 1
    fi
    
else
    print_error "Failed to submit build"
    exit 1
fi

print_success "Main extraction service deployment complete!"
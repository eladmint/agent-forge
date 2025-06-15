#!/bin/bash

# Agent Forge Website - Enterprise Deployment Script
# This script deploys the Agent Forge website using Google Cloud Build

set -e

# Configuration
PROJECT_ID="tokenhunter-457310"
REGION="us-central1"
BUILD_CONFIG="cloudbuild.yaml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔥 Agent Forge Website - Enterprise Deployment${NC}"
echo "=================================================="

# Verify we're in the right directory
if [ ! -f "package.json" ] || [ ! -f "cloudbuild.yaml" ]; then
    echo -e "${RED}❌ Error: Must be run from the website directory${NC}"
    exit 1
fi

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Error: gcloud CLI not found. Please install Google Cloud SDK${NC}"
    exit 1
fi

# Verify project access
echo -e "${YELLOW}🔍 Verifying project access...${NC}"
if ! gcloud projects describe "$PROJECT_ID" &> /dev/null; then
    echo -e "${RED}❌ Error: Cannot access project $PROJECT_ID${NC}"
    echo "Please ensure you have the correct permissions and project ID"
    exit 1
fi

# Set the project
gcloud config set project "$PROJECT_ID"

# Validate build configuration exists
echo -e "${YELLOW}🔍 Checking build configuration...${NC}"
if [ ! -f "$BUILD_CONFIG" ]; then
    echo -e "${RED}❌ Error: Build configuration file not found${NC}"
    exit 1
fi

# Create Cloud Storage bucket if it doesn't exist
echo -e "${YELLOW}🪣 Setting up Cloud Storage bucket...${NC}"
BUCKET_NAME="agent-forge-website-static"
if ! gsutil ls -b "gs://$BUCKET_NAME" &> /dev/null; then
    echo "Creating bucket $BUCKET_NAME..."
    gsutil mb -p "$PROJECT_ID" -l "$REGION" "gs://$BUCKET_NAME"
    
    # Make bucket publicly readable
    gsutil iam ch allUsers:objectViewer "gs://$BUCKET_NAME"
    
    # Set up web configuration
    gsutil web set -m index.html -e 404.html "gs://$BUCKET_NAME"
fi

# Run pre-deployment validation
echo -e "${YELLOW}🧪 Running pre-deployment validation...${NC}"

# Validate package.json
if ! npm run build --dry-run &> /dev/null; then
    echo -e "${RED}❌ Error: Build script validation failed${NC}"
    exit 1
fi

# Check for required environment variables
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ Error: PROJECT_ID environment variable not set${NC}"
    exit 1
fi

# Submit build to Cloud Build
echo -e "${YELLOW}🚀 Submitting build to Cloud Build...${NC}"
BUILD_ID=$(gcloud builds submit \
    --config="$BUILD_CONFIG" \
    --substitutions="_PROJECT_ID=$PROJECT_ID,_REGION=$REGION" \
    --format="value(id)")

echo -e "${GREEN}✅ Build submitted successfully!${NC}"
echo "Build ID: $BUILD_ID"
echo "Monitor build progress: https://console.cloud.google.com/cloud-build/builds/$BUILD_ID?project=$PROJECT_ID"

# Wait for build completion
echo -e "${YELLOW}⏳ Waiting for build completion...${NC}"
if gcloud builds log --stream "$BUILD_ID"; then
    echo -e "${GREEN}✅ Build completed successfully!${NC}"
    
    # Get the website URL
    WEBSITE_URL="https://storage.googleapis.com/$BUCKET_NAME/index.html"
    echo -e "${GREEN}🌐 Website deployed to: $WEBSITE_URL${NC}"
    
    # Optionally set up custom domain (commented out for now)
    # echo -e "${YELLOW}🌍 Setting up custom domain...${NC}"
    # gcloud compute url-maps create agent-forge-website-map --default-backend-bucket=agent-forge-website-backend
    
else
    echo -e "${RED}❌ Build failed!${NC}"
    echo "Check the build logs for details: https://console.cloud.google.com/cloud-build/builds/$BUILD_ID?project=$PROJECT_ID"
    exit 1
fi

echo -e "${GREEN}🎉 Agent Forge website deployment completed successfully!${NC}"
echo "=================================================="
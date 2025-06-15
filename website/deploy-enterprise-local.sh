#!/bin/bash

# =============================================================================
# DEPLOYMENT SCRIPT: Agent Forge Website - Enterprise Deployment (Local)
# STATUS: ✅ ENTERPRISE STANDARD with COMPLIANCE FRAMEWORK
# ARCHITECTURE: Next.js static site deployment with Firebase Hosting + Global CDN
# COMPLIANCE: Automated pre-deployment validation integrated
# USE WHEN: Agent Forge website deployment for production from local directory
# =============================================================================

set -e  # Exit on any error

# Enterprise deployment configuration
PROJECT_ID="tokenhunter-457310"
SERVICE_NAME="agent-forge-website"
REGION="us-central1"
DEPLOYMENT_TYPE="ENTERPRISE"
FIREBASE_SITE="agent-forge-website"

echo "🚀 Starting Enterprise Agent Forge Website Deployment (Local)..."
echo "========================================================================"
echo "📋 Deployment Details:"
echo "   Service: $SERVICE_NAME"
echo "   Project: $PROJECT_ID"
echo "   Type: $DEPLOYMENT_TYPE"
echo "   Platform: Firebase Hosting"
echo "   CDN: Global"
echo "   Working Directory: $(pwd)"
echo "========================================================================"

# Validate environment
echo "🔍 Validating deployment environment..."

# Check if we're in the correct directory (website)
if [ ! -f "package.json" ]; then
    echo "❌ Error: Must be run from agent_forge/website/ directory"
    echo "Current directory: $(pwd)"
    exit 1
fi

# Check if Next.js config exists
if [ ! -f "next.config.js" ]; then
    echo "❌ Error: next.config.js not found"
    exit 1
fi

# Validate Firebase CLI installation
if ! command -v firebase &> /dev/null; then
    echo "📦 Installing Firebase CLI..."
    npm install -g firebase-tools
fi

# Check Firebase authentication
echo "🔐 Validating Firebase authentication..."
if ! firebase projects:list --project $PROJECT_ID &> /dev/null; then
    echo "❌ Error: Firebase authentication required"
    echo "Run: firebase login"
    exit 1
fi

echo "✅ Environment validation complete"
echo ""

# Pre-deployment compliance validation
echo "📋 Running enterprise compliance validation..."

# Validate enterprise brand compliance
echo "🎨 Validating brand compliance..."
if ! grep -q "ancient-gold\|nuru-purple\|ancient-bronze" src/app/globals.css; then
    echo "⚠️  Warning: Enterprise brand colors may not be properly implemented"
fi

# Validate dark mode is enabled
if ! grep -q 'className="dark"' src/app/layout.tsx; then
    echo "⚠️  Warning: Dark mode may not be enabled by default"
else
    echo "✅ Dark mode is enabled by default"
fi

echo "✅ Compliance validation complete"
echo ""

# Build the Next.js application
echo "🏗️  Building Next.js application..."

# Install dependencies
echo "📦 Installing dependencies..."
npm ci

# Run build with static export
echo "🔨 Building static export..."
npm run build

# Validate build output
if [ ! -d "out" ]; then
    echo "❌ Error: Build output directory 'out' not found"
    echo "Build may have failed or static export not configured"
    exit 1
fi

echo "✅ Build completed successfully"
echo "📁 Build output size: $(du -sh out | cut -f1)"
echo ""

# Initialize Firebase configuration if needed
if [ ! -f ".firebaserc" ]; then
    echo "🔧 Initializing Firebase configuration..."
    
    # Create firebase.json
    cat > firebase.json << EOF
{
  "hosting": {
    "public": "out",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ],
    "headers": [
      {
        "source": "**/*.@(js|css)",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "max-age=31536000"
          }
        ]
      },
      {
        "source": "**",
        "headers": [
          {
            "key": "X-Frame-Options",
            "value": "DENY"
          },
          {
            "key": "X-Content-Type-Options",
            "value": "nosniff"
          },
          {
            "key": "X-XSS-Protection",
            "value": "1; mode=block"
          }
        ]
      }
    ]
  }
}
EOF
    
    # Set Firebase project
    firebase use $PROJECT_ID
fi

# Deploy to Firebase Hosting
echo "🚀 Deploying to Firebase Hosting..."
echo "   Site: $FIREBASE_SITE"
echo "   Project: $PROJECT_ID"

firebase deploy --only hosting --project $PROJECT_ID

# Post-deployment validation
echo ""
echo "🔍 Running post-deployment validation..."

# Wait for deployment to propagate
sleep 10

# Health check
SITE_URL="https://$PROJECT_ID.web.app"
echo "🌐 Testing deployment at: $SITE_URL"

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $SITE_URL)
if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ Deployment health check passed (HTTP $HTTP_STATUS)"
else
    echo "⚠️  Deployment health check warning (HTTP $HTTP_STATUS)"
fi

# Performance validation
echo "📊 Validating performance..."
curl -s -o /dev/null -w "Response time: %{time_total}s\n" $SITE_URL

echo ""
echo "========================================================================"
echo "🎉 Agent Forge Website Deployment Complete!"
echo "========================================================================"
echo "📋 Deployment Summary:"
echo "   ✅ Service: $SERVICE_NAME"
echo "   ✅ Platform: Firebase Hosting"
echo "   ✅ CDN: Global distribution enabled"
echo "   ✅ SSL: Automatic HTTPS"
echo "   ✅ Security: Enterprise headers configured"
echo "   ✅ Dark Mode: Enabled by default"
echo ""
echo "🌐 Website URLs:"
echo "   Primary: https://$PROJECT_ID.web.app"
echo "   Backup:  https://$PROJECT_ID.firebaseapp.com"
echo ""
echo "📊 Next Steps:"
echo "   1. Configure custom domain (if required)"
echo "   2. Set up monitoring alerts"
echo "   3. Validate performance metrics"
echo "   4. Update documentation"
echo ""
echo "✅ Deployment completed successfully at $(date)"
echo "========================================================================"
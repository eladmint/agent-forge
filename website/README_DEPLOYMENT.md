# Agent Forge Website - Enterprise Deployment Guide

## Overview

This document outlines the enterprise deployment process for the Agent Forge website, following the project's enterprise deployment standards defined in CLAUDE.md.

## Architecture

- **Framework**: Next.js 15 with static export
- **Styling**: Tailwind CSS with custom Agent Forge branding
- **Deployment**: Google Cloud Platform with Cloud Build
- **CDN**: Google Cloud Storage + Cloud CDN
- **Container**: Nginx-based Docker container for alternative deployment

## Enterprise Deployment Requirements

Following the mandatory enterprise deployment standards:

### ✅ Path Validation
All imports and paths have been validated for production deployment.

### ✅ Service Isolation
Website deployment is isolated from other services with no cross-service dependencies.

### ✅ Centralized Requirements
Uses centralized `package.json` in the website directory for all dependencies.

### ✅ Enterprise Configuration
Uses approved enterprise deployment scripts and configurations.

## Deployment Methods

### Method 1: Cloud Build + Cloud Storage (Recommended)

```bash
# From the website/ directory
./deploy-enterprise.sh
```

This script:
1. Validates the build configuration
2. Sets up Cloud Storage bucket with CDN
3. Submits build to Cloud Build
4. Deploys static files to Cloud Storage
5. Configures CDN caching

### Method 2: Docker Container Deployment

```bash
# Build the Docker image
docker build -t agent-forge-website .

# Run locally for testing
docker run -p 8080:80 agent-forge-website

# Deploy to Cloud Run
gcloud run deploy agent-forge-website \
    --image agent-forge-website \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

## Pre-Deployment Validation

Before deployment, the following validations are automatically performed:

1. **Build Validation**: `npm run build` must complete successfully
2. **Type Checking**: TypeScript compilation must pass
3. **Linting**: ESLint checks must pass
4. **Security**: Nginx security headers configured
5. **Performance**: Static assets optimized and compressed

## Configuration Files

### Core Files
- `cloudbuild.yaml` - Cloud Build configuration
- `deploy-enterprise.sh` - Enterprise deployment script
- `Dockerfile` - Container configuration
- `nginx.conf` - Web server configuration
- `.dockerignore` - Docker build optimization

### Build Configuration
- `next.config.js` - Next.js configuration with static export
- `tailwind.config.ts` - Tailwind CSS configuration
- `tsconfig.json` - TypeScript configuration

## Security Features

### Nginx Security Headers
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection: enabled
- Referrer-Policy: strict-origin-when-cross-origin

### Access Control
- Blocks access to sensitive files (.env, package.json, etc.)
- Denies access to hidden files and directories
- Health check endpoint at `/health`

## Monitoring and Observability

### Health Checks
- Health endpoint: `/health`
- Returns 200 status with "healthy" response

### Logging
- Nginx access logs to `/var/log/nginx/access.log`
- Error logs to `/var/log/nginx/error.log`
- Cloud Build logs available in GCP console

## Performance Optimization

### Static Asset Caching
- JavaScript/CSS: 1 year cache with immutable flag
- Images: 1 year cache with immutable flag
- HTML files: 1 hour cache

### Compression
- Gzip compression enabled for text-based assets
- Compression level 6 for optimal size/speed balance

## Domain Configuration

The deployment supports custom domain setup. To configure:

1. Set up Cloud Load Balancer
2. Configure SSL certificate
3. Update DNS records
4. Uncomment domain configuration in deploy script

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check Node.js version (requires 18+)
   - Verify all dependencies are installed
   - Check TypeScript compilation errors

2. **Deployment Failures**
   - Verify GCP project access
   - Check Cloud Build service account permissions
   - Ensure Cloud Storage bucket exists

3. **Runtime Issues**
   - Check nginx configuration syntax
   - Verify static files are properly copied
   - Check Docker container logs

### Support Commands

```bash
# View build logs
gcloud builds log [BUILD_ID]

# Check bucket contents
gsutil ls -la gs://agent-forge-website-static

# Test nginx configuration
nginx -t -c /path/to/nginx.conf

# Check container health
curl http://localhost:8080/health
```

## Environment Variables

Required for deployment:
- `PROJECT_ID`: GCP project ID (default: agent-forge-production)
- `REGION`: Deployment region (default: us-central1)

## Compliance

This deployment configuration follows:
- ✅ Enterprise deployment process enforcement
- ✅ ZERO-TOLERANCE POLICY validation requirements
- ✅ Production-ready security standards
- ✅ Performance optimization best practices

## Next Steps

After successful deployment:
1. Configure custom domain (optional)
2. Set up monitoring and alerting
3. Configure CDN optimizations
4. Set up backup and disaster recovery
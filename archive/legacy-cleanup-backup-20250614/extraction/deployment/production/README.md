# 🚀 Production Multi-Region Services

## 📋 **MAIN PRODUCTION DEPLOYMENT**

This directory contains the **production-ready** multi-region extraction services with complete Enhanced Orchestrator capabilities.

### ✅ **Production Services (USE THESE)**

#### **Enhanced Multi-Region Service**
- **File:** `services/enhanced_multi_region_service.py`
- **Purpose:** Complete multi-region extraction with 13+ agents
- **Capabilities:**
  - ✅ Complete Enhanced Orchestrator integration
  - ✅ Calendar discovery with LinkFinderAgent (90+ events)
  - ✅ All 13+ agent system coordination
  - ✅ Database integration with Supabase
  - ✅ Visual intelligence and crypto knowledge
  - ✅ Rate limiting evasion through regional IP rotation
  - ✅ Cost optimization with budget controls

#### **Deployment Configuration**
- **Docker:** `services/Dockerfile.enhanced-multi-region`
- **Cloud Build:** `deployment/cloudbuild.enhanced-multi-region.yaml`
- **Deploy Script:** `deployment/deploy_enhanced_multi_region_services.sh`

### 🚀 **Quick Deployment**

```bash
# Deploy complete production system
cd production/deployment
./deploy_enhanced_multi_region_services.sh
```

### 🎯 **Service URLs (After Deployment)**

- **US Central:** `https://enhanced-multi-region-us-central-867263134607.us-central1.run.app`
- **Europe West:** `https://enhanced-multi-region-europe-west-867263134607.europe-west1.run.app`

### 📊 **Testing Production Services**

```bash
# Health check
curl https://enhanced-multi-region-us-central-867263134607.us-central1.run.app/health

# Full extraction test
curl -X POST "https://enhanced-multi-region-us-central-867263134607.us-central1.run.app/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://lu.ma/ethcc"],
    "calendar_discovery": true,
    "save_to_database": false,
    "visual_intelligence": true
  }'
```

### 🔗 **Dashboard Integration**

The production services are designed to work with the dashboard:

```bash
# Run dashboard with production integration
streamlit run tools/dashboard.py
# Select: "🌐 Multi-Region Extraction" monitoring view
```

### ⚠️ **IMPORTANT NOTES**

1. **Use Enhanced Services:** Always use the enhanced services for production
2. **Complete Functionality:** These services include ALL capabilities described in architecture docs
3. **90+ Event Extraction:** Calendar discovery will find all events from calendar pages
4. **Database Integration:** Automatic saving with deduplication
5. **Cost Optimization:** Intelligent regional selection and budget management

### 🔍 **Difference from Test Services**

| Feature | Production Enhanced | Test Simplified |
|---------|-------------------|-----------------|
| **Agent System** | ✅ Complete 13+ agents | ❌ No agents |
| **Calendar Discovery** | ✅ LinkFinderAgent | ❌ Basic URL only |
| **Database Integration** | ✅ Supabase with deduplication | ❌ No database |
| **Event Extraction** | ✅ 90+ events | ❌ 0-17 events |
| **Visual Intelligence** | ✅ Advanced image analysis | ❌ None |
| **Rate Limiting Evasion** | ✅ Full regional switching | ❌ Basic health checks |

**Always use production services for real extraction tasks!**
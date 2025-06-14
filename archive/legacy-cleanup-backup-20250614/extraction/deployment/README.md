# Extraction Service Deployment

**Service**: Nuru AI Extraction Service  
**Last Updated**: November 30, 2024  
**Organization Status**: ✅ ENTERPRISE ORGANIZED

---

## 🎯 **Quick Start**

### **Primary Deployment (Recommended)**
```bash
# Production multi-region deployment
cd src/extraction/deployment/
./scripts/01_deploy_enhanced_multi_region.py
```

### **Alternative Deployments**
```bash
# Shell-based comprehensive deployment
./scripts/02_deploy_enhanced_multi_region.sh

# Proof of concept testing
./scripts/03_deploy_multi_region_poc.sh

# Legacy single-region service
./scripts/04_deploy_main_extraction_service.sh
```

---

## 📁 **Directory Structure**

```
src/extraction/deployment/
├── scripts/           # 🔧 EXECUTABLE DEPLOYMENT SCRIPTS
│   ├── 01_*          # Primary deployment method
│   ├── 02_*          # Comprehensive fallback
│   ├── 03_*          # Advanced/testing
│   └── 04_*          # Legacy support
├── configs/           # ⚙️ CONFIGURATION FILES
│   ├── 01_main_extraction.yaml      # Primary config
│   ├── 02_main_extractor.yaml       # Extractor config
│   ├── 03_enhanced_multi_region.yaml # Enhanced config
│   ├── 04_production_orchestrator.yaml # Production orchestrator
│   ├── cloudbuild/                   # Additional cloudbuild configs
│   ├── dockerfiles/                  # Docker configurations
│   │   ├── 01_*      # Primary production Dockerfiles
│   │   ├── 02_*      # Secondary configurations
│   │   └── specialized/              # Specialized variants
│   └── steel_browser/                # Steel Browser specific configs
│       └── 01_steel_browser_production.yaml
└── docs/              # 📚 DOCUMENTATION
    └── README.md      # This file
```

---

## 🚀 **Deployment Methods**

### **01 - Enhanced Multi-Region (Primary)**
- **Status**: ✅ PRIMARY RECOMMENDED
- **Architecture**: Multi-region extraction with production orchestrator
- **Use When**: Production deployments, high availability needed
- **Features**: Region redundancy, orchestrator coordination, database integration

### **02 - Enhanced Multi-Region Shell (Fallback)**
- **Status**: ✅ COMPREHENSIVE FALLBACK
- **Architecture**: Shell-based multi-region deployment
- **Use When**: CI/CD integration, automation scripts
- **Features**: Shell automation, comprehensive error handling

### **03 - Multi-Region POC (Advanced)**
- **Status**: ⚠️ ADVANCED USERS
- **Architecture**: Proof of concept deployment
- **Use When**: Testing concepts, prototype validation
- **Features**: Experimental features, concept validation

### **04 - Main Extraction Service (Legacy)**
- **Status**: 🔄 LEGACY SUPPORT
- **Architecture**: Single-region extraction service
- **Use When**: Legacy compatibility, simple deployments
- **Features**: Basic extraction, single region

---

## 🔧 **Configuration Management**

### **Primary Configurations**
- `01_main_extraction.yaml` - Main extraction service config
- `02_main_extractor.yaml` - Core extractor configuration
- `03_enhanced_multi_region.yaml` - Enhanced multi-region setup
- `04_production_orchestrator.yaml` - Production orchestrator

### **Steel Browser Integration** 🎯
- `steel_browser/01_steel_browser_production.yaml` - Production Steel Browser config
- `dockerfiles/05_Dockerfile.steel_browser_orchestrator` - Steel Browser Docker setup
- `dockerfiles/07_Dockerfile.enhanced_orchestrator_browser` - Browser-enabled orchestrator

### **Docker Configurations**
1. `01_Dockerfile.main_extraction` - Primary extraction
2. `02_Dockerfile.main_extractor` - Core extractor
3. `03_Dockerfile.multi_region` - Multi-region setup
4. `04_Dockerfile.multi_region_extractor` - Multi-region extractor
5. `05_Dockerfile.steel_browser_orchestrator` - Steel Browser
6. `06_Dockerfile.production_orchestrator` - Production orchestrator
7. `07_Dockerfile.enhanced_orchestrator_browser` - Browser-enabled
8. `08_Dockerfile.orchestrator` - Base orchestrator

---

## 🎯 **Steel Browser Implementation**

**IMPORTANT**: Steel Browser work should use this deployment structure exclusively:

```bash
# Steel Browser deployment
cd src/extraction/deployment/

# Use Steel Browser config
gcloud builds submit --config configs/steel_browser/01_steel_browser_production.yaml .

# Or use browser-enabled orchestrator
gcloud builds submit --config configs/cloudbuild/enhanced_orchestrator_browser.yaml .
```

**Do NOT use**: Root `/deployment` directory for Steel Browser work

---

## 📊 **Health Checks**

After deployment, verify services:

```bash
# Check service health
curl https://[SERVICE-URL]/health

# Check extraction capabilities
curl -X POST https://[SERVICE-URL]/extract \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://lu.ma/ethcc"], "save_to_database": true}'
```

---

## 🔗 **Related Documentation**

- [Enterprise Deployment Roadmap](../../../memory-bank/current-focus/ENTERPRISE_DEPLOYMENT_ROADMAP.md)
- [Deployment Migration Plan](../../../docs/reports/deployment/DEPLOYMENT_MIGRATION_PLAN.md)
- [API Service Deployment](../../api/deployment/README.md)
- [Telegram Bot Deployment](../../telegram_bot/deployment/README.md)

---

## 📝 **Migration Notes**

**Migrated from**: Root `/deployment` directory  
**Migration Date**: November 30, 2024  
**Migration Reason**: Enterprise service-centric organization  

**Original Locations**:
- Scripts: `/deployment/deploy_*` → `scripts/`
- Configs: `/deployment/cloudbuild.*` → `configs/`
- Dockerfiles: `/deployment/docker/Dockerfile.*` → `configs/dockerfiles/`

**Benefits**:
- ✅ Service isolation and clear ownership
- ✅ Numbered priority system for deployments
- ✅ Unblocked Steel Browser implementation
- ✅ Enterprise-grade organization and scalability 
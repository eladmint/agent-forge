# 🚀 Nuru AI Extraction Service

**Last Updated:** June 9, 2025
**Version:** 9.0 (Unified Scraper Service)

Welcome to the Nuru AI Extraction Service. This service is responsible for discovering and extracting event data from a wide variety of web sources using a unified, multi-tier architecture.

**📖 SINGLE SOURCE OF TRUTH:** For a complete architectural overview, please see:
- **[UNIFIED_SCRAPER_ARCHITECTURE.md](../../docs/architecture/components/UNIFIED_SCRAPER_ARCHITECTURE.md)**

---

## 🏗️ Core Architecture: Unified Scraper Service v9.0

The service is built on a **unified, multi-tier architecture**. This means there is a single entry point for all extraction tasks, which intelligently routes requests to the most appropriate processing tier based on website complexity. The core logic is managed by the `UnifiedExtractionOrchestrator`.

### Tiers of Operation
- **Tier 1 (HTTP):** For simple, static sites that don't require JavaScript rendering.
- **Tier 2 (Playwright):** For dynamic sites requiring JavaScript execution.
- **Tier 3 (Steel Browser MCP):** For complex sites that are protected by anti-bot measures, requiring advanced browser automation.

---

## 🚀 Getting Started

### Production Extraction

The primary script for running a full, production-level extraction is `run_unified_ethcc_extraction.py`. This script is configured to process a calendar URL, discover all event links, and then perform detailed extraction on each one.

```bash
# Activate the virtual environment
source venv_unified/bin/activate

# Run the unified extraction for the EthCC calendar
python src/extraction/scripts/production/run_unified_ethcc_extraction.py
```

### Development & Testing

Developers can interact with the various components of the extraction service. Refer to the architecture document for details on individual agents and orchestrators.

---

## 📁 Directory Structure

The `src/extraction/` directory is organized to reflect the unified architecture:

```
src/extraction/
├── 🎯 orchestrators/                 # Orchestration Systems
│   └── unified_extraction_orchestrator.py # ✅ SINGLE SOURCE OF TRUTH
├── 🤖 agents/                       # Specialized, modular processing agents
├── ⚙️ components/                     # Core, reusable extraction components
├── 📜 scripts/                       # Runnable scripts
│   └── production/
│       └── run_unified_ethcc_extraction.py # ✅ PRIMARY PRODUCTION SCRIPT
└── 🧪 tests/                         # Unit and integration tests
```

---

## ☁️ Deployment

The Unified Scraper Service is deployed as a single containerized application on Google Cloud Run. The production service that contains this logic is the `steel-browser-orchestrator`.

**Note:** The old `production-orchestrator` service is now deprecated and should not be used.

### Health Check

To check the health of the deployed service, you can use the following command (replace with the correct service URL once deployed):
```bash
# Example health check
curl https://steel-browser-orchestrator-xxxxxxxx-uc.a.run.app/health
```

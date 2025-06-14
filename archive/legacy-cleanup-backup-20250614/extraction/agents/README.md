# 🤖 Nuru AI Extraction Agents

**Purpose:** This directory contains the core, specialized agents for the **Unified Scraper Service v9.0**. These agents perform specific, modular tasks within the multi-tier extraction process, from discovering links on a calendar page to executing complex browser automation.

**📖 COMPLETE ARCHITECTURE REFERENCE:** For the authoritative technical specification on how these agents are orchestrated, see:
- **[📋 UNIFIED_SCRAPER_ARCHITECTURE.md](../../docs/architecture/components/UNIFIED_SCRAPER_ARCHITECTURE.md)**

---

## 🏗️ Current Architecture: Unified Scraper Service

The agents in this directory are components of a single, unified service. They are no longer part of a standalone "Main Extractor" or "Enhanced Orchestrator." Instead, they are orchestrated by the `UnifiedExtractionOrchestrator` as part of a multi-tier strategy.

**Key Agent Roles in the Unified Architecture:**
- **Discovery:** The `LinkFinderAgent` is responsible for processing calendar-style pages to find all individual event URLs.
- **Extraction:** A suite of agents handles the actual data extraction, with the `IntelligentTierRouter` selecting the appropriate one based on website complexity:
    - **Tier 1 (HTTP):** Basic HTML parsing.
    - **Tier 2 (Playwright):** For JS-heavy sites, using the `PageScraperAgent`.
    - **Tier 3 (Steel Browser):** For protected sites, using the `MCPEnhancedScraperAgent`.
- **Processing:** Agents like the `DataCompilerAgent` and `EventDataRefinerAgent` clean, validate, and enrich the extracted data.

## 📁 Directory Organization

This directory contains the concrete implementations of the agents described in the architecture. Developers should refer to the `UNIFIED_SCRAPER_ARCHITECTURE.md` to understand how each agent fits into the overall data flow.

### 🎯 Core Production Agents (Active)
-   `event_data_extractor_agent.py`: Core HTML/JSON-LD parsing.
-   `advanced_visual_intelligence_agent.py`: Advanced image processing for floor plans, booth mapping, etc.
-   `data_compiler_agent.py`: Multi-source data consolidation and validation.
-   `event_data_refiner_agent.py`: Cleans and enhances extracted data using AI.
-   `experimental/link_finder_agent.py`: Discovers event links from calendar pages.
-   `experimental/page_scraper_agent.py`: Handles Tier 2 Playwright-based extraction.
-   `mcp_enhanced_scraper_agent.py`: Handles Tier 3 Steel Browser MCP-based extraction.
-   `experimental/super_enhanced_scraper_agent.py`: Contains the logic for the `IntelligentTierRouter`.

---

## 📚 Related Documentation

-   **Architecture:** `docs/architecture/components/UNIFIED_SCRAPER_ARCHITECTURE.md`
-   **Main Orchestrator Logic:** `src/extraction/orchestrators/unified_extraction_orchestrator.py`
-   **Production Script:** `src/extraction/scripts/production/run_unified_ethcc_extraction.py`
-   **Technology Context:** `memory-bank/07-techContext.md`
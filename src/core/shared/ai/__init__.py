"""
Agent Forge Module

This package provides modular AI functionality for the Agent Forge project,
replacing the monolithic ai_helpers.py with focused, maintainable modules.

Modules:
- embeddings: Text embedding generation and operations
- tokens: Token counting and usage tracking
- prompts: Prompt templates and generation
- schemas: Data schemas and validation
- config: Configuration and constants
"""

# Import key functions for backward compatibility
from .config import (
    DEFAULT_EMBEDDING_MODEL_ID,
    DEFAULT_TOKEN_MODEL,
    EMBEDDING_SIMILARITY_THRESHOLDS,
    MAX_PROMPT_CHARS,
    get_api_config,
    get_model_config,
    get_quality_config,
)

# Phase 2: Enhanced date processing functionality
from .date_processing import (
    DEFAULT_TIMEZONE,
    EnhancedDateProcessor,
    enhanced_get_events_by_date,
)
from .embeddings import (
    cosine_similarity,
    generate_embedding,  # Alias for backward compatibility
    generate_vertex_embedding_async,
    init_embedding_model,
    validate_embedding,
)

# Phase 2: Event filtering functionality
from .event_filtering import EventFilter, filter_events_smart
from .prompts import (
    PromptTemplate,
    create_content_classification_prompt,
    create_event_summary_prompt,
    create_gemini_prompt,
    create_speaker_extraction_prompt,
    truncate_text_smart,
)

# Search Quality Improvements functionality
from .query_enhancement import (
    QueryAnalysis,
    QueryComplexity,
    QueryEnhancer,
    QueryIntent,
    analyze_and_enhance_query,
)
from .relevance_scoring import (
    AdvancedRelevanceScorer,
    RelevanceFactors,
    RelevanceScore,
    score_and_rank_results,
)
from .schemas import (
    event_data_schema,
    get_empty_event_data,
    normalize_event_data,
    validate_event_data,
)
from .tokens import (
    TokenCounter,
    count_tokens,
    count_tokens_batch,
    estimate_tokens_simple,
    is_within_token_limit,
    truncate_to_token_limit,
)

# Version information
__version__ = "1.0.0"
__description__ = "Modular AI functionality for Agent Forge"

# Export main functions for direct import
__all__ = [
    # Embeddings
    "generate_vertex_embedding_async",
    "generate_embedding",
    "init_embedding_model",
    "validate_embedding",
    "cosine_similarity",
    # Tokens
    "count_tokens",
    "count_tokens_batch",
    "estimate_tokens_simple",
    "is_within_token_limit",
    "truncate_to_token_limit",
    "TokenCounter",
    # Prompts
    "create_gemini_prompt",
    "create_speaker_extraction_prompt",
    "create_event_summary_prompt",
    "create_content_classification_prompt",
    "truncate_text_smart",
    "PromptTemplate",
    # Schemas
    "event_data_schema",
    "validate_event_data",
    "get_empty_event_data",
    "normalize_event_data",
    # Config
    "DEFAULT_EMBEDDING_MODEL_ID",
    "DEFAULT_TOKEN_MODEL",
    "MAX_PROMPT_CHARS",
    "EMBEDDING_SIMILARITY_THRESHOLDS",
    "get_model_config",
    "get_api_config",
    "get_quality_config",
    # Date Processing (Phase 2)
    "EnhancedDateProcessor",
    "enhanced_get_events_by_date",
    "DEFAULT_TIMEZONE",
    # Event Filtering (Phase 2)
    "EventFilter",
    "filter_events_smart",
    # Search Quality Improvements
    "QueryEnhancer",
    "QueryAnalysis",
    "QueryIntent",
    "QueryComplexity",
    "analyze_and_enhance_query",
    "AdvancedRelevanceScorer",
    "RelevanceScore",
    "RelevanceFactors",
    "score_and_rank_results",
]

# Module metadata
MODULE_INFO = {
    "created": "2025-05-30",
    "task": "Task 47: AI Helpers Restructuring + Phase 2: Functional Enhancements",
    "purpose": "Modularize monolithic ai_helpers.py into focused components with enhanced functionality",
    "modules": {
        "embeddings": "Text embedding generation and operations",
        "tokens": "Token counting and usage tracking",
        "prompts": "Prompt templates and generation",
        "schemas": "Data schemas and validation",
        "config": "Configuration and constants",
        "date_processing": "Enhanced date parsing and natural language processing (Phase 2)",
        "event_filtering": "Smart event filtering for improved search relevance (Phase 2)",
        "query_enhancement": "Advanced query understanding and enhancement for better search intent detection",
        "relevance_scoring": "Multi-factor relevance scoring system for improved search result ranking",
    },
    "backward_compatibility": True,
    "original_file": "utils/ai_helpers.py (213 lines)",
    "new_structure": "8 focused modules with enhanced functionality",
    "phase2_enhancements": "Enhanced date-based search with natural language support + Smart event filtering for improved search relevance",
    "search_quality_improvements": "Advanced query understanding with intent detection + Multi-factor relevance scoring for better result ranking",
}

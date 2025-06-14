"""
AI Helpers - Backward Compatibility Module

This module provides AI integration utilities for the Agent Forge framework
while delegating to the new modular ai package structure.

DEPRECATED: This module is maintained for backward compatibility only.
New code should import directly from .utils.ai submodules:

- utils.ai.embeddings for embedding operations
- utils.ai.tokens for token counting
- utils.ai.prompts for prompt templates
- utils.ai.schemas for data schemas
- utils.ai.config for configuration

Original file: 213 lines -> Now: Modular structure with 5 focused modules
Task 47: AI Helpers Restructuring - Completed May 30, 2025
"""

import logging
import warnings

from .ai.config import (
    DEFAULT_EMBEDDING_MODEL_ID,
    DEFAULT_TOKEN_MODEL,
    EMBEDDING_SIMILARITY_THRESHOLDS,
    get_api_config,
    get_model_config,
)
from .ai.embeddings import (
    DEFAULT_EMBEDDING_MODEL_ID as EMBEDDING_MODEL_ID,  # Backward compatibility alias
)

# Import all functions from the new modular structure
from .ai.embeddings import (
    cosine_similarity,
    generate_vertex_embedding_async,
    init_embedding_model,
    validate_embedding,
)
from .ai.prompts import MAX_PROMPT_CHARS, create_gemini_prompt, truncate_text_smart
from .ai.schemas import event_data_schema, normalize_event_data, validate_event_data
from .ai.tokens import (
    count_tokens,
    estimate_tokens_simple,
    is_within_token_limit,
    truncate_to_token_limit,
)

logger = logging.getLogger(__name__)

# Backward compatibility aliases
generate_embedding = generate_vertex_embedding_async  # Most common alias


# Issue deprecation warning for direct imports from this module
def _issue_deprecation_warning():
    """Issue a deprecation warning for old import patterns."""
    warnings.warn(
        "Direct imports from .ai_helpers are deprecated. "
        "Please use utils.ai submodules instead: "
        "utils.ai.embeddings, utils.ai.tokens, utils.ai.prompts, "
        "utils.ai.schemas, utils.ai.config",
        DeprecationWarning,
        stacklevel=3,
    )


# Monkey-patch the imports to issue warnings
_original_getattr = globals().get("__getattribute__", None)


def __getattribute__(name):
    """Override attribute access to issue deprecation warnings."""
    # List of functions that should trigger deprecation warnings
    deprecated_functions = [
        "generate_vertex_embedding_async",
        "generate_embedding",
        "init_embedding_model",
        "count_tokens",
        "create_gemini_prompt",
        "event_data_schema",
    ]

    if name in deprecated_functions and name in globals():
        _issue_deprecation_warning()

    if _original_getattr:
        return _original_getattr(name)
    else:
        return globals()[name]


# For compatibility, re-export all the original constants and functions
__all__ = [
    # Embeddings (from .ai.embeddings)
    "generate_vertex_embedding_async",
    "generate_embedding",
    "init_embedding_model",
    "EMBEDDING_MODEL_ID",  # Backward compatibility
    "DEFAULT_EMBEDDING_MODEL_ID",
    "validate_embedding",
    "cosine_similarity",
    # Tokens (from .ai.tokens)
    "count_tokens",
    "estimate_tokens_simple",
    "is_within_token_limit",
    "truncate_to_token_limit",
    # Prompts (from .ai.prompts)
    "create_gemini_prompt",
    "MAX_PROMPT_CHARS",
    "truncate_text_smart",
    # Schemas (from .ai.schemas)
    "event_data_schema",
    "validate_event_data",
    "normalize_event_data",
    # Config (from .ai.config)
    "DEFAULT_TOKEN_MODEL",
    "EMBEDDING_SIMILARITY_THRESHOLDS",
    "get_model_config",
    "get_api_config",
]

# Module information for debugging and tracking
_MODULE_INFO = {
    "status": "deprecated_but_functional",
    "task": "Task 47: AI Helpers Restructuring",
    "completion_date": "2025-05-30",
    "original_lines": 213,
    "new_structure": "5 modular files in utils/ai/",
    "migration_path": {
        "embeddings": "utils.ai.embeddings",
        "tokens": "utils.ai.tokens",
        "prompts": "utils.ai.prompts",
        "schemas": "utils.ai.schemas",
        "config": "utils.ai.config",
    },
    "backward_compatibility": True,
    "deprecation_warnings": True,
}


def get_module_info():
    """
    Get information about the AI helpers module restructuring.

    Returns:
        dict: Module restructuring information
    """
    return _MODULE_INFO.copy()


def show_migration_guide():
    """
    Display migration guide for updating imports.
    """
    print(
        """
    🔄 AI Helpers Migration Guide (Task 47)
    
    OLD (Deprecated):
    from .ai_helpers import generate_embedding, count_tokens, create_gemini_prompt
    
    NEW (Recommended):
    from .ai.embeddings import generate_vertex_embedding_async as generate_embedding
    from .ai.tokens import count_tokens
    from .ai.prompts import create_gemini_prompt
    
    Or use the package-level imports:
    from .utils.ai import generate_embedding, count_tokens, create_gemini_prompt
    
    Benefits of new structure:
    ✅ Modular organization (5 focused modules vs 1 monolithic file)
    ✅ Enhanced functionality (validation, batch processing, caching)
    ✅ Better testing and maintenance
    ✅ Clear separation of concerns
    ✅ Backward compatibility maintained
    
    Modules created:
    📁 utils/ai/embeddings.py - Text embedding operations
    📁 utils/ai/tokens.py - Token counting and estimation  
    📁 utils/ai/prompts.py - Prompt templates and generation
    📁 utils/ai/schemas.py - Data schemas and validation
    📁 utils/ai/config.py - Configuration and constants
    """
    )


# Log the restructuring information
logger.info(
    f"AI Helpers restructuring completed: {_MODULE_INFO['original_lines']} lines -> {_MODULE_INFO['new_structure']}"
)
logger.info(
    "Backward compatibility maintained. Consider migrating to utils.ai submodules."
)

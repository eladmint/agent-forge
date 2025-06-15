"""
Token counting functionality for Agent Forge operations.

This module handles token counting operations using Google's Generative AI models
for accurate token usage tracking and prompt optimization.
"""

import functools
import logging
from typing import Any, Dict, List

import anyio
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Default token counting configuration
DEFAULT_TOKEN_MODEL = "gemini-1.5-flash-latest"
MAX_PROMPT_CHARS = 30000  # Maximum characters for prompt processing


async def count_tokens(text: str, model: str = DEFAULT_TOKEN_MODEL) -> int:
    """
    Counts tokens using the Gemini API.

    Args:
        text: The text to count tokens for
        model: The model to use for token counting (defaults to gemini-1.5-flash-latest)

    Returns:
        int: Number of tokens in the text, or 0 if counting failed

    Raises:
        None: Exceptions are caught and logged, returns 0 on error
    """
    if not text or not isinstance(text, str):
        logger.warning("Cannot count tokens for empty or invalid text.")
        return 0

    try:
        client = genai.Client()

        # Use async wrapper for thread safety
        count_tokens_partial = functools.partial(
            client.models.count_tokens, model=model, contents=[text]
        )
        response = await anyio.to_thread.run_sync(count_tokens_partial)

        token_count = response.total_tokens
        logger.debug(f"Token count for text ({len(text)} chars): {token_count} tokens")
        return token_count

    except Exception as e:
        logger.error(f"Error counting tokens: {e}", exc_info=True)
        return 0


async def count_tokens_batch(
    texts: List[str], model: str = DEFAULT_TOKEN_MODEL
) -> List[int]:
    """
    Count tokens for multiple texts efficiently.

    Args:
        texts: List of texts to count tokens for
        model: The model to use for token counting

    Returns:
        List[int]: Token counts for each text in the same order
    """
    if not texts:
        return []

    # Process each text individually for now
    # Could be optimized with batch API calls in the future
    token_counts = []
    for text in texts:
        count = await count_tokens(text, model)
        token_counts.append(count)

    return token_counts


def estimate_tokens_simple(text: str) -> int:
    """
    Provide a simple token estimate without API calls.

    This is a rough estimation based on character count and common
    tokenization patterns. Use for quick estimates when API calls
    are not desired.

    Args:
        text: The text to estimate tokens for

    Returns:
        int: Estimated number of tokens
    """
    if not text:
        return 0

    # Rough estimation: ~4 characters per token for English text
    # This is an approximation and actual token count may vary
    estimated_tokens = len(text) // 4

    # Account for spaces and punctuation
    word_count = len(text.split())
    estimated_tokens = max(estimated_tokens, word_count)

    return estimated_tokens


def is_within_token_limit(
    text: str, token_limit: int, use_estimate: bool = False
) -> bool:
    """
    Check if text is within a specified token limit.

    Args:
        text: The text to check
        token_limit: Maximum allowed tokens
        use_estimate: If True, use simple estimation instead of API call

    Returns:
        bool: True if within limit, False otherwise
    """
    if use_estimate:
        token_count = estimate_tokens_simple(text)
        return token_count <= token_limit

    # For accurate checking, you'd need to await count_tokens()
    # This function provides a synchronous interface for estimates
    return estimate_tokens_simple(text) <= token_limit


def truncate_to_token_limit(
    text: str, token_limit: int, use_estimate: bool = True
) -> str:
    """
    Truncate text to approximately fit within a token limit.

    Args:
        text: The text to truncate
        token_limit: Maximum allowed tokens
        use_estimate: Whether to use estimation (True) or exact counting (False)

    Returns:
        str: Truncated text that should fit within the token limit
    """
    if not text:
        return text

    if use_estimate:
        estimated_tokens = estimate_tokens_simple(text)
        if estimated_tokens <= token_limit:
            return text

        # Estimate character limit based on token limit
        estimated_char_limit = token_limit * 4  # Rough estimation

        # Truncate and try to break at word boundaries
        if len(text) <= estimated_char_limit:
            return text

        truncated = text[:estimated_char_limit]

        # Try to break at last word boundary
        last_space = truncated.rfind(" ")
        if last_space > estimated_char_limit * 0.8:  # If we can keep 80% of content
            truncated = truncated[:last_space]

        return truncated

    # For exact truncation, you'd need async token counting
    # Fall back to estimation for now
    return truncate_to_token_limit(text, token_limit, use_estimate=True)


class TokenCounter:
    """
    A class for managing token counting operations with caching.
    """

    def __init__(self, model: str = DEFAULT_TOKEN_MODEL):
        self.model = model
        self._cache: Dict[str, int] = {}
        self._cache_size_limit = 1000  # Limit cache size

    async def count(self, text: str, use_cache: bool = True) -> int:
        """
        Count tokens with optional caching.

        Args:
            text: Text to count tokens for
            use_cache: Whether to use/update cache

        Returns:
            int: Token count
        """
        if use_cache and text in self._cache:
            return self._cache[text]

        count = await count_tokens(text, self.model)

        if use_cache and len(self._cache) < self._cache_size_limit:
            self._cache[text] = count

        return count

    def clear_cache(self):
        """Clear the token count cache."""
        self._cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cache_size": len(self._cache),
            "cache_limit": self._cache_size_limit,
            "model": self.model,
        }

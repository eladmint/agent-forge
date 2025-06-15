"""
Embedding generation functionality for Agent Forge operations.

This module handles all embedding-related operations including text embedding
generation using Google's Generative AI models.
"""

import functools
import logging
from typing import List, Optional

import anyio
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Default embedding model configuration
DEFAULT_EMBEDDING_MODEL_ID = "models/text-embedding-004"
DEFAULT_MAX_LENGTH = 2048  # Safe limit for text-embedding-004


def init_embedding_model():
    """
    Ensures the Google API key is available for embedding operations.

    Note: This function assumes the API key has been configured globally
    via genai.configure(api_key=...) elsewhere in the application.
    """
    logger.info("Checked for GOOGLE_API_KEY for embedding model.")


async def generate_vertex_embedding_async(
    text_content: str,
    model_name: Optional[str] = None,
    max_length: int = DEFAULT_MAX_LENGTH,
) -> Optional[List[float]]:
    """
    Generates an embedding for the given text using Google's Generative AI model.

    Args:
        text_content: The text to generate embeddings for
        model_name: Optional model name to use (defaults to DEFAULT_EMBEDDING_MODEL_ID)
        max_length: Maximum text length before truncation (defaults to 2048)

    Returns:
        List[float]: The embedding vector, or None if generation failed

    Raises:
        None: Exceptions are caught and logged, returns None on error
    """
    if not text_content or not isinstance(text_content, str):
        logger.warning("Cannot generate embedding for empty or invalid text content.")
        return None

    # Truncate text if too long
    truncated_text = text_content[:max_length]
    if len(text_content) > max_length:
        logger.debug(
            f"Truncating text content for embedding from {len(text_content)} to {max_length} chars."
        )

    try:
        current_model_id = model_name if model_name else DEFAULT_EMBEDDING_MODEL_ID

        logger.debug(
            f"Generating embedding for text snippet: {truncated_text[:100]}... using {current_model_id}"
        )

        # Asynchronous call using anyio.to_thread for thread safety
        embed_content_partial = functools.partial(
            genai.embed_content,
            model=current_model_id,
            content=truncated_text,
            task_type="RETRIEVAL_QUERY",
        )
        result = await anyio.to_thread.run_sync(embed_content_partial)

        # Validate and extract embedding from result
        if (
            result
            and isinstance(result, dict)
            and "embedding" in result
            and isinstance(result["embedding"], list)
        ):
            logger.debug(
                f"Successfully generated embedding (dimension: {len(result['embedding'])})"
            )
            return result["embedding"]
        else:
            logger.warning(f"Unexpected result format from embed_content API: {result}")
            return None

    except Exception as e:
        logger.error(f"Error calling Google Embedding API: {e}", exc_info=True)
        return None


# Backward compatibility alias
generate_embedding = generate_vertex_embedding_async


def validate_embedding(embedding: Optional[List[float]]) -> bool:
    """
    Validate that an embedding is properly formatted.

    Args:
        embedding: The embedding to validate

    Returns:
        bool: True if embedding is valid, False otherwise
    """
    return (
        embedding is not None
        and isinstance(embedding, list)
        and len(embedding) > 0
        and all(isinstance(x, (int, float)) for x in embedding)
    )


def get_embedding_dimension(embedding: Optional[List[float]]) -> int:
    """
    Get the dimension of an embedding vector.

    Args:
        embedding: The embedding vector

    Returns:
        int: The dimension of the embedding, or 0 if invalid
    """
    if validate_embedding(embedding):
        return len(embedding)
    return 0


def normalize_embedding(embedding: List[float]) -> List[float]:
    """
    Normalize an embedding vector to unit length.

    Args:
        embedding: The embedding vector to normalize

    Returns:
        List[float]: The normalized embedding vector
    """
    if not validate_embedding(embedding):
        return embedding

    # Calculate magnitude
    magnitude = sum(x * x for x in embedding) ** 0.5

    if magnitude == 0:
        return embedding

    # Normalize to unit length
    return [x / magnitude for x in embedding]


def cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """
    Calculate cosine similarity between two embeddings.

    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector

    Returns:
        float: Cosine similarity between -1 and 1, or 0 if invalid inputs
    """
    if not (validate_embedding(embedding1) and validate_embedding(embedding2)):
        return 0.0

    if len(embedding1) != len(embedding2):
        logger.warning(
            f"Embedding dimension mismatch: {len(embedding1)} vs {len(embedding2)}"
        )
        return 0.0

    # Calculate dot product and magnitudes
    dot_product = sum(a * b for a, b in zip(embedding1, embedding2, strict=False))
    magnitude1 = sum(a * a for a in embedding1) ** 0.5
    magnitude2 = sum(b * b for b in embedding2) ** 0.5

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)

import logging
import os

from dotenv import load_dotenv

# Logging setup
logger = logging.getLogger(__name__)

# For typed constants from Vertex AI
try:
    from vertexai.generative_models import (
        GenerationConfig,
        HarmBlockThreshold,
        HarmCategory,
    )
except ImportError:
    # Define dummy classes for IDE type checking if imports fail
    class GenerationConfig:
        def __init__(self, **kwargs):
            pass

    class HarmCategory:
        HARM_CATEGORY_HARASSMENT = "HARM_CATEGORY_HARASSMENT"
        HARM_CATEGORY_HATE_SPEECH = "HARM_CATEGORY_HATE_SPEECH"
        HARM_CATEGORY_SEXUALLY_EXPLICIT = "HARM_CATEGORY_SEXUALLY_EXPLICIT"
        HARM_CATEGORY_DANGEROUS_CONTENT = "HARM_CATEGORY_DANGEROUS_CONTENT"

    class HarmBlockThreshold:
        BLOCK_MEDIUM_AND_ABOVE = "BLOCK_MEDIUM_AND_ABOVE"


# Load environment variables from .env file
load_dotenv()

# API Version Constants
API_VERSION_V1 = "/v1"
API_VERSION_V2 = "/v2"

# Service Information
SERVICE_NAME = "Agent Forge API"
SERVICE_VERSION = "2.1.0"
PROJECT_NAME = "Agent Forge"
PROJECT_VERSION = os.getenv("PROJECT_VERSION", "1.0.0")


# Function to read secrets from mounted files, environment variables, or use default
def get_secret(secret_name, env_var_name=None, default_value=None):
    """
    Read a secret value from mounted files first, then environment variables, then default value.

    Args:
        secret_name: Name of the secret in Secret Manager (filename in /etc/secrets)
        env_var_name: Name of the environment variable (defaults to secret_name if None)
        default_value: Default value if neither secret file nor env var exists
    """
    if env_var_name is None:
        env_var_name = secret_name

    # Try to read from mounted secret file
    try:
        with open(f"/etc/secrets/{secret_name}", "r") as f:
            return f.read().strip()
    except (FileNotFoundError, IOError):
        # Fall back to environment variable
        return os.getenv(env_var_name, default_value)


# API Keys and Project Configuration
GOOGLE_API_KEY = get_secret("GOOGLE_API_KEY")
SUPABASE_URL = get_secret("SUPABASE_URL")
SUPABASE_KEY = get_secret("SUPABASE_KEY")
TELEGRAM_BOT_TOKEN = get_secret("TELEGRAM_BOT_TOKEN")
VERTEX_PROJECT_ID = get_secret("VERTEX_PROJECT_ID", default_value="agent-forge-project")
VERTEX_LOCATION = get_secret("VERTEX_LOCATION", default_value="us-central1")
VERTEX_MODEL_NAME = get_secret(
    "VERTEX_MODEL_NAME",
    default_value="gemini-2.0-flash-001",  # Stable working model
)
MODEL_NAME_LONG = "gemini-2.0-flash-001"  # Stable working model

# OAuth Configuration
GOOGLE_CLIENT_ID = get_secret("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_CLIENT_SECRET = get_secret("GOOGLE_OAUTH_CLIENT_SECRET")
OAUTH_REDIRECT_URI = get_secret(
    "OAUTH_REDIRECT_URI",
    default_value="https://chatbot-api-service-v2-oo6mrfxexq-uc.a.run.app/auth/callback/google",
)


# Helper function to clean environment variable values
def clean_env_value(var_name, default_value):
    """Clean environment variable value by removing comments and whitespace"""
    value = os.environ.get(var_name, default_value)
    if isinstance(value, str) and "#" in value:
        value = value.split("#")[0].strip()
    return value


# LLM configuration defaults with fallbacks
DEFAULT_VERTEX_PROJECT_ID = VERTEX_PROJECT_ID
DEFAULT_VERTEX_LOCATION = VERTEX_LOCATION
DEFAULT_VERTEX_MODEL_NAME = VERTEX_MODEL_NAME
DEFAULT_VERTEX_METHOD = clean_env_value("VERTEX_METHOD", "generate_content")
DEFAULT_TEMPERATURE = float(clean_env_value("TEMPERATURE", "0.2"))
DEFAULT_MAX_OUTPUT_TOKENS = int(clean_env_value("MAX_OUTPUT_TOKENS", "1024"))
DEFAULT_TOP_P = float(clean_env_value("TOP_P", "0.95"))
DEFAULT_TOP_K = int(clean_env_value("TOP_K", "40"))

# Debug mode and CORS configuration
debug_value = clean_env_value("DEBUG", "false")
DEBUG = debug_value.lower() in ("true", "1", "t", "yes")
ALLOW_ORIGINS = clean_env_value("ALLOW_ORIGINS", "*").split(",")

# Logging configuration
LOG_LEVEL = clean_env_value("LOG_LEVEL", "INFO").upper()

# Additional feature flags
USE_TEST_MODE = clean_env_value("USE_TEST_MODE", "false").lower() in (
    "true",
    "1",
    "t",
    "yes",
)
BYPASS_CREDIT_CHECK = clean_env_value("BYPASS_CREDIT_CHECK", "false").lower() in (
    "true",
    "1",
    "t",
    "yes",
)

# Security configuration
SECURITY_ENABLED = clean_env_value("SECURITY_ENABLED", "true").lower() in (
    "true",
    "1",
    "t",
    "yes",
)
API_KEY_ENABLED = clean_env_value("API_KEY_ENABLED", "false").lower() in (
    "true",
    "1",
    "t",
    "yes",
)
RATE_LIMIT_ENABLED = clean_env_value("RATE_LIMIT_ENABLED", "true").lower() in (
    "true",
    "1",
    "t",
    "yes",
)
SECURITY_HEADERS_ENABLED = clean_env_value(
    "SECURITY_HEADERS_ENABLED", "true"
).lower() in (
    "true",
    "1",
    "t",
    "yes",
)


# Define interaction types and default messages
class InteractionType:
    QUERY = "query"
    CHAT = "chat"
    WEBHOOK = "webhook"
    UNKNOWN_INTERACTION = "unknown_interaction"
    LLM_CALL_ERROR = "llm_call_error"
    LLM_EMPTY_RESPONSE_ERROR = "llm_empty_response_error"
    LLM_TOOL_REQUEST = "llm_tool_request"
    LLM_SYNTHESIS_AFTER_TOOL = "llm_synthesis_after_tool"
    LLM_DIRECT_RESPONSE = "llm_direct_response"
    LLM_MAX_ITERATIONS_FALLBACK = "llm_max_iterations_fallback"
    INTERNAL_SERVER_ERROR = "internal_server_error"


class DefaultMessages:
    THINKING = "I'm thinking about that..."
    ERROR = "Sorry, I encountered an error. Please try again."
    NOT_UNDERSTOOD = "I'm sorry, I didn't understand your query. Could you rephrase it?"
    INSUFFICIENT_CREDITS = "You have insufficient credits to use this service. Please contact support to add more credits."


# System prompts
SYSTEM_PROMPT_V2 = """
You are an AI assistant for Agent Forge, a comprehensive crypto/Web3 event intelligence platform.
Your goal is to help users find information about events, speakers, and organizations across major crypto conferences including Token2049, EthCC, Devcon, and other blockchain events.
Respond to user queries by using the available tools to search for events, speakers, organizations, or session details from our comprehensive database.
"""

CHATBOT_SYSTEM_INSTRUCTION = (
    "You are Agent Forge Bot, a helpful assistant for comprehensive crypto/Web3 event intelligence! 🤖 "
    "You have access to comprehensive tools to search events, speakers, and organizations from major crypto conferences including Token2049, EthCC, Devcon, and other blockchain events. "
    "Additionally, you can search external websites when users specifically request it (e.g., 'search ethglobal.com for events'). "
    "Be friendly, engaging, and use emojis. For date queries, you can intelligently interpret dates like 'April 20' "
    "by assuming the current year context. Use the available tools to provide accurate, real-time information "
    "about crypto events, speakers, and organizations from our comprehensive database, or search external sites when requested. Always provide helpful and specific information when possible."
)
MODEL_SYSTEM_ACKNOWLEDGEMENT = "I understand. I will use the comprehensive crypto event database tools to provide accurate information from real event data including Token2049, EthCC, Devcon, and other blockchain conferences, and can also search external websites when specifically requested."  # Response the model should give to the system prompt


# Embedding model for semantic search
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "text-embedding-004")

# Regex patterns
SPEAKER_NAME_PATTERN = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z'-]+)+)\b"  # Pattern to find potential speaker names (two capitalized words)

# Supabase Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL"
)  # Typically constructed from other Supabase vars or set directly

# Application Settings (Placeholder - structure might be more complex)
# Attempt to get it from an environment variable, otherwise default to an empty dict.
# This would ideally be loaded from a JSON string in env var or a separate config file.
APP_SETTINGS = os.getenv("APP_SETTINGS", {})

# Limits and thresholds
MAX_CONTEXT_LENGTH_TOKENS = int(clean_env_value("MAX_CONTEXT_LENGTH_TOKENS", "7000"))
MAX_HISTORY_ITEMS = 20  # Default based on previous MAX_HISTORY_ITEMS_VERTEX
MAX_TOOL_ITERATIONS = 5
INITIAL_CREDITS = 100  # Default credits for new users

# Performance and Database Configuration
DATABASE_POOL_SIZE = int(clean_env_value("DATABASE_POOL_SIZE", "10"))
DATABASE_MAX_OVERFLOW = int(clean_env_value("DATABASE_MAX_OVERFLOW", "20"))
DATABASE_POOL_TIMEOUT = int(clean_env_value("DATABASE_POOL_TIMEOUT", "30"))
DATABASE_POOL_RECYCLE = int(clean_env_value("DATABASE_POOL_RECYCLE", "3600"))

# Caching Configuration
CACHE_ENABLED = clean_env_value("CACHE_ENABLED", "true").lower() in (
    "true",
    "1",
    "t",
    "yes",
)
CACHE_TTL_EMBEDDINGS = int(clean_env_value("CACHE_TTL_EMBEDDINGS", "3600"))  # 1 hour
CACHE_TTL_SEARCH_RESULTS = int(
    clean_env_value("CACHE_TTL_SEARCH_RESULTS", "300")
)  # 5 minutes
CACHE_TTL_TOOL_RESULTS = int(
    clean_env_value("CACHE_TTL_TOOL_RESULTS", "600")
)  # 10 minutes
REDIS_URL = clean_env_value("REDIS_URL", "redis://localhost:6379")

# Performance Optimization Settings
ASYNC_POOL_SIZE = int(clean_env_value("ASYNC_POOL_SIZE", "20"))
TOOL_EXECUTION_TIMEOUT = int(clean_env_value("TOOL_EXECUTION_TIMEOUT", "30"))
BATCH_REQUEST_SIZE = int(clean_env_value("BATCH_REQUEST_SIZE", "5"))
ENABLE_REQUEST_BATCHING = clean_env_value(
    "ENABLE_REQUEST_BATCHING", "true"
).lower() in ("true", "1", "t", "yes")

# Chat Behavior
DEFAULT_ERROR_MESSAGE = (
    "Sorry, I encountered an issue while processing your request. "
    "Please try again later."
)
MAX_ITERATIONS_FALLBACK_MESSAGE = (
    f"I've used my tools {MAX_TOOL_ITERATIONS + 1} times but couldn't finalize an answer. "
    "Can you try rephrasing?"
)

# Tool Configuration
TOOL_CONFIG = None  # Placeholder, handled dynamically in the application code

# Vertex AI Generation Configuration
try:
    GENERATION_CONFIG = GenerationConfig(
        temperature=0.2,
        max_output_tokens=2048,
        top_p=0.95,
        top_k=40,
    )

    # Standard Safety Settings
    SAFETY_SETTINGS = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    }
except ImportError:
    logger.critical(
        "CRITICAL: Failed to import required classes from vertexai.generative_models. "
        "GENERATION_CONFIG and SAFETY_SETTINGS will be dictionaries. "
        "This may lead to runtime errors if the SDK expects its own class instances. "  # noqa: E501
        "Ensure the Vertex AI SDK is installed correctly and all dependencies are met."
    )
    # Fallback if Vertex AI imports failed
    GENERATION_CONFIG = {
        "temperature": 0.2,
        "max_output_tokens": 2048,
        "top_p": 0.95,
        "top_k": 40,
    }
    SAFETY_SETTINGS = {}

# Pricing Constants
GEMINI_FLASH_PRICE_PER_1K_CHARS_INPUT = 0.000125
GEMINI_FLASH_PRICE_PER_1K_CHARS_OUTPUT = 0.000125
EMBEDDING_PRICE_PER_1K_CHARS = 0.00002

# Ensure all imported variables are defined
if SUPABASE_KEY is None:
    # main.py also tries to read SUPABASE_KEY, let's try that as a fallback for SUPABASE_KEY
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Log configuration at startup
logger.info(
    f"Configuration loaded: DEBUG={DEBUG}, "
    f"VERTEX_PROJECT_ID={DEFAULT_VERTEX_PROJECT_ID}, "
    f"VERTEX_MODEL_NAME={DEFAULT_VERTEX_MODEL_NAME}"
)

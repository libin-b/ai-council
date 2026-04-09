import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# config.py
# Configuration for AI Discussion Room

# Your Gemini API key (Loaded from environment for security)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL_ID = "gemini-3-flash-preview" # Reverting to stable version
GEMINI_MODEL = GEMINI_MODEL_ID       # Alias for compatibility

# Local Models to use (Ollama)
OLLAMA_MODELS = [
    "llama3.2:3b",        # Reverted from 1b to default/latest
    "qwen2.5-coder:7b",# Reverted from 1.5b to 7b (confirmed installed)
    "mistral:7b",         # Standard mistral
    "deepseek-v3.1:671b-cloud",
    "gpt-oss:120b-cloud",
    "qwen3-coder:480b-cloud"
]

# Settings
CONCURRENCY = 1  # Run models one at a time (safe for beginners)
TIMEOUT = 120    # Wait up to 2 minutes per model
ENABLE_GOOGLE_SEARCH = True # 🔍 Enable Google Search for Gemini


# Fallback Priority (Best to Worst for Moderator role)
# Matches the display names (e.g. "Deepseek-v3.1", "Mistral", "Llama3.2")
MODERATOR_PRIORITY = [
    "Deepseek-v3.1",
    "Mistral",
    "Llama3.2",
    "Qwen2.5-coder"
]

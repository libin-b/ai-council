import os

# config.py
# Configuration for AI Discussion Room

# Your Gemini API key (replace with your actual key)
GEMINI_API_KEY = "AIzaSyCwUdqfKf3-XtvsbvOn4O2V63pzcxO_ENk"
GEMINI_MODEL_ID = "gemini-2.5-flash" # Reverting to stable version
# Local Models to use (Ollama)
LOCAL_MODELS = [
    "llama3.2:3b",        # Reverted from 1b to default/latest
    "qwen2.5-coder:7b",# Reverted from 1.5b to 7b (confirmed installed)
    "mistral:7b",         # Standard mistral
    "deepseek-v3.1:671b-cloud"
    # "deepseek-r1:1.5b" # Unsure if installed, commenting out to be safe
]

# Settings
CONCURRENCY = 1  # Run models one at a time (safe for beginners)
TIMEOUT = 120    # Wait up to 2 minutes per model

# Fallback Priority (Best to Worst for Moderator role)
# Matches the display names (e.g. "Deepseek-v3.1", "Mistral", "Llama3.2")
MODERATOR_PRIORITY = [
    "Deepseek-v3.1",
    "Mistral",
    "Llama3.2",
    "Qwen2.5-coder"
]

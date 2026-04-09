import asyncio
from typing import Optional
from google import genai
from google.genai import types
from .base import BaseModel

class GeminiModel(BaseModel):
    """Gemini 2.5 Flash implementation."""

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        super().__init__("Gemini")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    async def generate_response(self, prompt: str) -> str:
        """Generates response using Gemini API with retry logic."""
        print(f"🔮 Gemini receiving prompt...")
        max_retries = 3
        # Run the synchronous API call in a thread to keep main loop non-blocking
        # standard asyncio.to_thread is good for IO bound sync calls
        for attempt in range(max_retries):
            try:
                # Check for Search Config (imported dynamically or passed in)
                tools_config = None
                from config import ENABLE_GOOGLE_SEARCH 
                if ENABLE_GOOGLE_SEARCH:
                     # Correct format for google-genai SDK v1.0+
                     tools_config = [types.Tool(google_search=types.GoogleSearch())]

                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(tools=tools_config) if tools_config else None 
                )
                return response.text
            except Exception as e:
                is_quota = "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e)
                if is_quota and attempt < max_retries - 1:
                    wait_time = 10 * (attempt + 1)
                    await asyncio.sleep(wait_time)
                    continue
                # Simplify error message for UI
                error_msg = str(e)
                if "429" in error_msg:
                    return "❌ Gemini Error: Rate Limit Exceeded (429)"
                elif "404" in error_msg:
                    return "❌ Gemini Error: Model Not Found (404)"
                else:
                    # Keep it short, first 50 chars of error
                    return f"❌ Gemini Error: {error_msg[:100]}..."
        return "❌ Gemini Error: Quota exhausted."

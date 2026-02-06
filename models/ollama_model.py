import asyncio
import ollama
from .base import BaseModel

class OllamaModel(BaseModel):
    """Local Ollama model implementation."""

    def __init__(self, model_name: str):
        # Clean up name for display (e.g., "llama3.2:3b" -> "Llama3.2")
        display_name = model_name.split(":")[0].capitalize()
        super().__init__(display_name)
        self.model_id = model_name

    async def generate_response(self, prompt: str) -> str:
        """Generates response using local Ollama instance with retry logic."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # ollama.chat is synchronous, so we run it in a separate thread
                response = await asyncio.to_thread(
                    ollama.chat,
                    model=self.model_id,
                    messages=[{'role': 'user', 'content': prompt}],
                    options={'num_ctx': 8192}  # Increase context to 8k to prevent truncation
                )
                return response['message']['content']
            except Exception as e:
                # Check for rate limits (429) or service unavailable (503) usually in the error string
                error_str = str(e)
                if "429" in error_str or "503" in error_str or "try again" in error_str.lower():
                    if attempt < max_retries - 1:
                        wait_time = 5 * (attempt + 1)
                        # We print to stderr or just silent wait, usually good to let user know if it's long
                        # But for now we'll just sleep. 
                        # To avoid messing up the UI spinner, we just sleep.
                        await asyncio.sleep(wait_time)
                        continue
                return f"❌ {self.model_id} Error: {str(e)[:50]}..."
        return f"❌ {self.name} Error: Retries exhausted."

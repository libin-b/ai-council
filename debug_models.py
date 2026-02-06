import asyncio
from config import GEMINI_API_KEY
from models.gemini import GeminiModel
from models.ollama_model import OllamaModel

async def test_models():
    print("Testing Gemini...")
    try:
        gemini = GeminiModel(api_key=GEMINI_API_KEY)
        resp = await gemini.generate_response("Hello, say hi!")
        print(f"Gemini Response: {resp}")
    except Exception as e:
        print(f"Gemini Failed: {e}")

    print("\nTesting Ollama (Llama3.2)...")
    try:
        llama = OllamaModel("llama3.2:3b")
        resp = await llama.generate_response("Hello, say hi!")
        print(f"Llama Response: {resp}")
    except Exception as e:
        print(f"Llama Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_models())

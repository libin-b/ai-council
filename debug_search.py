import asyncio
from config import GEMINI_API_KEY
from models.gemini import GeminiModel

async def test_search():
    print("Defaulting to Search Mode...")
    gemini = GeminiModel(api_key=GEMINI_API_KEY)
    
    # Query meant to trigger search
    query = "What is the current stock price of Google (GOOGL) right now?"
    print(f"Query: {query}")
    
    resp = await gemini.generate_response(query)
    print(f"\nResponse:\n{resp}")

if __name__ == "__main__":
    asyncio.run(test_search())

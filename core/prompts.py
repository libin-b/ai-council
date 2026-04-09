# Prompts for the AI Discussion Room

ROUND_1_PROMPT = """You are an expert AI assistant taking part in a technical discussion.
Question: {question}

Provide a clear, concise, and accurate response. Focus on being helpful and technically correct.
"""

ROUND_2_CRITIQUE_PROMPT = """You are an expert reviewer.
User Question: {question}

Here are responses from other AI models:
{other_responses}

Please critique these responses:
1. Identify any errors or inaccuracies.
2. Point out what they did well.
3. Suggest an improved solution combining the best parts.

Keep your critique constructive and concise.
"""

ROUND_3_SYNTHESIS_PROMPT = """You are the moderator of an AI council.
User Question: {question}

Here are the initial responses and critiques from the panel:

{all_data}

Your task is to synthesize the FINAL ANSWER.
1. Combine the most accurate information from all models.
2. Resolve any disagreements based on technical facts.
3. Provide the single best possible answer to the user's question.
4. If code is requested, provide the final corrected code.

CRITICAL INSTRUCTIONS:
- You MUST use the following format:
---REASONING---
(Briefly explain your synthesis process, why you chose certain points, and how you resolved conflicts. Be concise.)
---FINAL ANSWER---
(The actual answer to the user. Direct and helpful.)

- The "Final Answer" must be independent and not reference the reasoning section.
- If the answer is simple (e.g., a greeting), the reasoning can be very short (e.g., "Standard greeting").
"""

def format_for_critique(results: dict, question: str = "") -> str:
    """Helper to format multiple model results into the critique prompt."""
    other_responses_text = ""
    for name, resp in results.items():
        # Truncate to avoid context window explosion if many models
        snippet = resp[:2000] 
        other_responses_text += f"\n--- Response from {name} ---\n{snippet}\n"
    
    return ROUND_2_CRITIQUE_PROMPT.format(question=question, other_responses=other_responses_text)

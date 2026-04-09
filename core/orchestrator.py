import asyncio
from typing import List, Dict
import core.prompts as prompts
from core.prompts import ROUND_1_PROMPT, ROUND_2_CRITIQUE_PROMPT, ROUND_3_SYNTHESIS_PROMPT
from models.base import BaseModel

class Orchestrator:
    def __init__(self, models: List[BaseModel], moderator: BaseModel):
        self.models = models
        self.moderator = moderator # Usually Gemini for synthesis

    async def conduct_discussion(self, question: str, progress_callback=None, **kwargs) -> Dict:
        """
        Runs the full 3-phase discussion.
        Returns a dictionary with full conversation logs.
        """
        
        # --- Round 1: Gather Initial Responses ---
        if progress_callback: progress_callback("Round 1: Gathering initial responses...")
        
        # Helper to wrap model execution with identity
        async def fetch_response(model, prompt):
            resp = await model.generate_response(prompt)
            return model, resp

        round1_tasks = []
        for model in self.models:
            prompt = ROUND_1_PROMPT.format(question=question)
            round1_tasks.append(fetch_response(model, prompt))
            
        # Process results as they complete
        results_r1 = {}
        for future in asyncio.as_completed(round1_tasks):
            model, resp = await future
            results_r1[model.name] = resp
            
            # Notify callback if provided (streaming output)
            if "on_round1_result" in kwargs:
                kwargs["on_round1_result"](model.name, resp)
        
        # Sort results to maintain consistent order in internal logs if needed, 
        # but results_r1 is a dict so key access is fine.

        
        # --- Round 2: Critique ---
        if progress_callback: progress_callback("Round 2: Critiquing peers...")

        # Filter out error messages so we don't ask models to critique "Error 404"
        valid_results = {k: v for k, v in results_r1.items() if not v.strip().startswith("❌")}
        
        if len(valid_results) < 2:
            # Not enough valid responses to debate
            critique_prompt = "Not enough valid responses for a debate."
            critiques = {}
        else:
            # Assuming 'prompts' is an object or module with a format_for_critique method
            # This might require an additional import or definition of 'prompts'
            # For now, we'll assume it's available in the scope or will be handled by the user.
            # Assuming 'prompts' is an object or module with a format_for_critique method
            critique_prompt = prompts.format_for_critique(valid_results, question=question)
            
            # Wrapper to keep track of which model is critiquing
            async def fetch_critique(model, prompt):
                resp = await model.generate_response(prompt)
                return model, resp

            critique_tasks = []
            for model in self.models:
                # OPTIMIZATION: If a model failed in Round 1 (not in valid_results), 
                # do not ask it to critique. It likely has connection/quota issues.
                if model.name not in valid_results:
                    continue

                critique_tasks.append(fetch_critique(model, critique_prompt))

            critiques = {}
            for future in asyncio.as_completed(critique_tasks):
                model, resp = await future
                critiques[model.name] = resp
                
                # Notify callback if provided
                if "on_round2_result" in kwargs:
                    kwargs["on_round2_result"](model.name, resp)

        # Assign critiques to results_r2 for consistency with original structure
        results_r2 = critiques

        # --- Round 3: Synthesis ---
        if progress_callback: progress_callback("Round 3: Synthesizing final answer...")

        # Compile all data for the moderator
        all_data_text = "--- INITIAL RESPONSES ---\n"
        for name, resp in results_r1.items():
            all_data_text += f"\n[{name}]:\n{resp}\n"
            
        all_data_text += "\n--- CRITIQUES ---\n"
        for name, resp in results_r2.items():
            all_data_text += f"\n[{name} Critique]:\n{resp}\n"

        synthesis_prompt = ROUND_3_SYNTHESIS_PROMPT.format(question=question, all_data=all_data_text)
        
        # Try moderator first
        final_answer = await self.moderator.generate_response(synthesis_prompt)
        
        # Fallback Logic: If moderator fails (e.g. 429 Rate Limit), try other capable models
        if final_answer.strip().startswith("❌"):
            print(f"\n⚠️ Moderator {self.moderator.name} failed. Attempting fallback...")
            
            # Import priority from config, or default to empty list
            try:
                from config import MODERATOR_PRIORITY
            except ImportError:
                MODERATOR_PRIORITY = []

            # Sort models by priority
            sorted_models = sorted(
                self.models, 
                key=lambda m: MODERATOR_PRIORITY.index(m.name) if m.name in MODERATOR_PRIORITY else 999
            )

            for fallback_model in sorted_models:
                # Don't ask the failed moderator again
                if fallback_model.name == self.moderator.name:
                    continue
                
                print(f"🔄 Trying {fallback_model.name} as moderator...")
                fallback_answer = await fallback_model.generate_response(synthesis_prompt)
                
                if not fallback_answer.strip().startswith("❌"):
                    final_answer = fallback_answer
                    break
            else:
                final_answer = "❌ All models failed to synthesize an answer."

        # Parse Structured Output if available
        reasoning = "Check 'Synthesis Prompt' for raw input."
        actual_final_answer = final_answer
        
        if "---FINAL ANSWER---" in final_answer:
            parts = final_answer.split("---FINAL ANSWER---")
            if len(parts) >= 2:
                # Part 0 might be reasoning or preamble
                preamble = parts[0].replace("---REASONING---", "").strip()
                if preamble:
                    reasoning = preamble
                
                # Part 1 is the actual answer
                actual_final_answer = parts[1].strip()

        return {
            "question": question,
            "round1": results_r1,
            "round2": results_r2,
            "final_answer": actual_final_answer,
            "moderator_reasoning": reasoning, # New field for UI
            "synthesis_prompt": synthesis_prompt 
        }

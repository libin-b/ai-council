import asyncio
import sys
from config import GEMINI_API_KEY, LOCAL_MODELS, GEMINI_MODEL_ID
from models.gemini import GeminiModel
from models.ollama_model import OllamaModel
from core.orchestrator import Orchestrator
from ui.console import UI, console
from rich.progress import Progress, SpinnerColumn, TextColumn

async def main_async():
    UI.print_header()
    
    # Initialize Models
    UI.print_step("Initializing models...")
    gemini_model = GeminiModel(api_key=GEMINI_API_KEY, model_name=GEMINI_MODEL_ID)
    
    models = [gemini_model]
    for model_name in LOCAL_MODELS:
        models.append(OllamaModel(model_name))
        
    console.print(f"[dim]Loaded {len(models)} models: {[m.name for m in models]}[/dim]")

    while True:
        try:
            print()
            question = UI.get_user_input("What is your question? (or 'q' to quit): ")
            if question.lower() in ['q', 'quit', 'exit']:
                break
                
            orchestrator = Orchestrator(models=models, moderator=gemini_model)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                
                # We need to wrap the orchestrator callback to update the progress bar
                task_id = progress.add_task("Starting discussion...", total=None)
                
                def update_progress(msg):
                    progress.update(task_id, description=msg)

                def on_model_response(name, response):
                    progress.stop()  # Pause spinner to print clean output
                    UI.print_model_response(name, response)
                    progress.start() # Resume spinner

                # Run the discussion
                logs = await orchestrator.conduct_discussion(
                    question, 
                    progress_callback=update_progress,
                    on_round1_result=on_model_response
                )
            
            # Display Results
            UI.print_step("Discussion Complete!")
            
            # Show Round 1 Summary
            UI.print_results(logs['round1'])
            
            # Show Final Answer
            UI.print_markdown(logs['final_answer'], title="🏆 Final Consensus Answer", style="green")
            
            # Option to see details
            if UI.get_user_input("Show critiques? (y/n): ").lower() == 'y':
                for model, critique in logs['round2'].items():
                    UI.print_markdown(critique, title=f"Critique by {model}", style="red")

        except KeyboardInterrupt:
            console.print("\n[bold red]🛑 Force stopping...[/bold red]")
            sys.exit(0)
        except Exception as e:
            console.print_exception()

def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        console.print("\n[bold red]👋 Goodbye![/bold red]")

if __name__ == "__main__":
    main()
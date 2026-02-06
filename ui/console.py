from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from rich.rule import Rule
from rich.panel import Panel # Keep just in case, though we are removing usage

console = Console()

class UI:
    @staticmethod
    def print_header():
        console.print(Panel.fit("[bold cyan]🤖 AI Discussion Room v2.0[/bold cyan]\n[dim]Multi-Model Consensus System[/dim]", border_style="cyan"))

    @staticmethod
    def get_user_input(prompt_text: str) -> str:
        console.print(f"[bold green]💬 {prompt_text}[/bold green]", end=" ")
        try:
            return input()
        except EOFError:
            return "q"

    @staticmethod
    def print_markdown(content: str, title: str = "", style: str = "white"):
        console.print(Rule(title, style=style))
        console.print(Markdown(content))
        console.print(Rule(style=style))

    @staticmethod
    def print_step(text: str):
        console.print(f"[bold yellow]➤ {text}[/bold yellow]")
        
    @staticmethod
    def print_results(results: dict):
        table = Table(title="Model Responses Summary")
        table.add_column("Model", style="cyan", no_wrap=True)
        table.add_column("Response Preview", style="white")
        
        for model_name, response in results.items():
            preview = response[:100].replace("\n", " ") + "..."
            table.add_row(model_name, preview)
            
        console.print(table)

    @staticmethod
    def print_model_response(model_name: str, response: str):
        """Prints a single model response using Rule separators (easier to copy-paste)."""
        console.print(Rule(f"🤖 {model_name}", style="blue"))
        console.print(Markdown(response))
        console.print("\n")

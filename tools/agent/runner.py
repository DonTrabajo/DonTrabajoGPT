import typer
from rich.console import Console
from dotenv import load_dotenv
from .agent.chain import Agent

app = typer.Typer(add_completion=False)
console = Console()

@app.command()
def chat(prompt: str):
    """One-shot query to the local agent."""
    load_dotenv(dotenv_path="tools/agent/.env", override=False)
    agent = Agent.from_env()
    final = agent.run(prompt)
    console.print("\n[bold green]Final Answer:[/bold green]")
    console.print(final)

@app.command()
def repl():
    """Interactive multi-turn REPL."""
    load_dotenv(dotenv_path="tools/agent/.env", override=False)
    agent = Agent.from_env()
    console.print("[bold cyan]Local OSS Agent REPL[/bold cyan] — type 'exit' to quit.")
    while True:
        try:
            user = input("\nYou: ").strip()
        except EOFError:
            break
        if user.lower() in {"exit", "quit"}:
            break
        final = agent.run(user)
        console.print("\n[bold green]Final Answer:[/bold green]")
        console.print(final)

if __name__ == "__main__":
    app()

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

console = Console()

def animated_transition():
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console
    ) as progress:
        progress.add_task(description="Analyzing with Don Trabajo GPT...", total=None)
        time.sleep(1.5)  # Simulate loading time


import json
from rich.console import Console
from rich.panel import Panel

console = Console()

def parse_linpeas_output(file_path):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)

        console.print(Panel("[bold cyan]linPEAS Output Summary[/bold cyan]", border_style="bright_green"))

        # Example: Look for interesting users or SUID binaries
        interesting_users = data.get("interesting_users", [])
        if interesting_users:
            console.print("[bold yellow]Interesting Users:[/bold yellow]")
            for user in interesting_users:
                console.print(f"🔸 {user}")

        suid_binaries = data.get("suid_binaries", [])
        if suid_binaries:
            console.print("\n[bold yellow]SUID Binaries:[/bold yellow]")
            for binary in suid_binaries:
                console.print(f"🛠  {binary}")

        # Placeholder: Add more parsing logic here
        if not interesting_users and not suid_binaries:
            console.print("[green]No high-interest data found (yet).[/green]")

    except FileNotFoundError:
        console.print(f"[red]❌ File not found: {file_path}[/red]")
    except json.JSONDecodeError:
        console.print(f"[red]❌ Invalid JSON format in: {file_path}[/red]")

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()


def show_main_menu():
    console.clear()

    console.print(
        Panel.fit(
            "[bold cyan]Don Trabajo GPT[/bold cyan]\n[i]CyberOps Console Interface[/i]",
            border_style="bright_magenta",
        )
    )

    table = Table(show_header=True, header_style="bold green")
    table.add_column("Option", style="dim", width=8)
    table.add_column("Feature")
    table.add_column("Status")

    menu_options = [
        ["0", "Preprocess linPEAS Raw Output", "🆕"],
        ["1", "Parse linPEAS Output", "✅ Ready"],
        ["2", "Run CVE Matcher", "✅ Ready"],
        ["3", "Tool Path Validation", "✅ Ready"],
        ["4", "HTB Log Tracker", "Coming Soon"],
        ["5", "Launch Discord Bot", "Coming Soon"],
        ["6", "Offline LLM (Local Persona)", "Beta"],
        ["7", "Full linPEAS Analyzer (combo)", "Beta"],
        ["8", "Exit", ""],
    ]

    for opt in menu_options:
        table.add_row(*opt)

    console.print(table)

    choice = Prompt.ask(
        "[bold yellow]Choose an option[/bold yellow]",
        choices=[opt[0] for opt in menu_options],
    )
    return choice

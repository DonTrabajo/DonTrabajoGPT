import os
from rich.console import Console
from rich.panel import Panel
import orchestrator

console = Console()


def analyze_linpeas_full_stack(raw_txt_path):
    """
    Deprecated legacy entrypoint.

    Use orchestrator.analyze_linpeas() instead; this wrapper keeps legacy CLI flows working.
    """
    console.print(Panel("[bold magenta]💻 Starting Full Stack linPEAS Analysis[/bold magenta]", border_style="bright_magenta"))
    result = orchestrator.analyze_linpeas(raw_txt_path, mode="auto", save_json=False)

    if result["status"] in {"success", "partial"}:
        console.print(Panel("[bold cyan]📜 Parsed Summary[/bold cyan]", border_style="bright_cyan"))
        parsed = result.get("parsed_data") or {}
        for user in parsed.get("users", []):
            console.print(f"• user: {user}")
        for suid in parsed.get("suid_binaries", []):
            console.print(f"• suid: {suid}")

        console.print(Panel("[bold yellow]🛡 CVE Matcher Results[/bold yellow]", border_style="yellow"))
        for finding in result.get("cve_findings", []):
            console.print(f"- {finding['name']} {finding['version']}: {finding['cve']} {finding['description']}")

        if result.get("llm_summary"):
            console.print(Panel(result["llm_summary"], title="🧠 LLM Summary", border_style="blue"))
    else:
        console.print(Panel(f"[red]Analysis failed: {result.get('errors')}[/red]", border_style="red"))


if __name__ == "__main__":
    from sys import argv

    if len(argv) != 2:
        console.print("[red]✗ Usage: python combo_linpeas_analyzer.py <linpeas_output.txt>[/red]")
    else:
        analyze_linpeas_full_stack(argv[1])

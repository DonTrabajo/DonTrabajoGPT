import os
import time
from rich.console import Console
from rich.panel import Panel
from don_trabajo_gpt_tui import show_main_menu
from validate_tool_paths import validate_tool_paths
from animated_transition import animated_transition
from swoosh_transition import swoosh_transition
from linpeas_parser import parse_linpeas_output
import orchestrator

console = Console()


def _prompt_for_file(prompt: str) -> str:
    """Prompt for a file path and ensure it exists before continuing."""
    path = input(prompt).strip()
    if not os.path.isfile(path):
        console.print("\a", style="bold red", end="")
        console.print(f"✗ File not found: {path}", style="bold red")
        input("\n[Press Enter to return to menu]")
        console.print(Panel("[green]Returning to menu...[/green]", border_style="bright_blue"))
        time.sleep(1)
        console.clear()
        return ""
    return path


def main():
    while True:
        choice = show_main_menu()

        if choice == "0":
            file_path = _prompt_for_file("📄 Preprocess raw linPEAS .txt to JSON: ")
            if not file_path:
                continue
            result = orchestrator.preprocess_only(file_path)
            if result["status"] == "success":
                console.print(Panel(f"[green]✓ JSON saved to:[/green] {result['json_path']}", border_style="green"))
            else:
                console.print(Panel(f"[red]✗ Preprocess failed:[/red] {result.get('error')}", border_style="red"))
            input("\n[Press Enter to return to menu]")
            swoosh_transition()

        elif choice == "1":
            file_path = _prompt_for_file("📄 Enter path to linPEAS JSON output file: ")
            if not file_path:
                continue
            console.print("\a", end="")
            animated_transition()
            parse_linpeas_output(file_path)
            console.print("\a", style="green", end="")
            input("\n[Press Enter to return to menu]")
            swoosh_transition()

        elif choice == "2":
            file_path = _prompt_for_file("📄 Enter path to linPEAS JSON output file: ")
            if not file_path:
                continue
            console.print("\a", end="")
            animated_transition()
            cve_result = orchestrator.run_cve_pipeline(file_path)
            if cve_result["status"] == "success" and cve_result.get("cve_findings"):
                for hit in cve_result["cve_findings"]:
                    console.print(f"• {hit['name']} {hit['version']} -> {hit['cve']}: {hit['description']}")
            elif cve_result["status"] == "success":
                console.print("[yellow]No CVE findings.[/yellow]")
            else:
                console.print(f"[red]✗ CVE matcher failed: {cve_result.get('error')}[/red]")
            console.print("\a", style="green", end="")
            input("\n[Press Enter to return to menu]")
            swoosh_transition()

        elif choice == "3":
            validate_tool_paths()
            console.print("\a", style="green", end="")
            input("\n[Press Enter to return to menu]")
            swoosh_transition()

        elif choice == "4":
            console.print("📝 HTB Log Tracker is coming soon.", style="cyan")
            input("\n[Press Enter to return to menu]")
            console.print(Panel("[green]Returning to menu...[/green]", border_style="bright_blue"))
            time.sleep(1)
            console.clear()

        elif choice == "5":
            console.print("🤖 Discord Bot launch feature not wired yet.", style="cyan")
            input("\n[Press Enter to return to menu]")
            console.print(Panel("[green]Returning to menu...[/green]", border_style="bright_blue"))
            time.sleep(1)
            console.clear()

        elif choice == "6":
            orchestrator.launch_agent_session(persona="don_trabajo", mode="local")
            input("\n[Press Enter to return to menu]")
            swoosh_transition()

        elif choice == "7":
            file_path = _prompt_for_file("📄 Enter path to raw linPEAS .txt for full-stack analysis: ")
            if not file_path:
                continue
            include_knowledge_input = input("Include internal knowledgebase in analysis? [y/N]: ").strip().lower()
            include_knowledge = include_knowledge_input == "y"
            animated_transition()
            result = orchestrator.analyze_linpeas(
                file_path,
                mode="auto",
                save_json=False,
                include_knowledge=include_knowledge,  # hook for future Knowledgebase enrichment
            )
            if result["status"] in {"success", "partial"}:
                console.print(Panel("[green]✓ Analysis complete[/green]", border_style="green"))
                parsed = result.get("parsed_data") or {}
                if parsed:
                    console.print("[bold yellow]Parsed Summary:[/bold yellow]")
                    for user in parsed.get("users", []):
                        console.print(f"• user: {user}")
                    for suid in parsed.get("suid_binaries", []):
                        console.print(f"• suid: {suid}")
                if result.get("cve_findings"):
                    console.print("[bold yellow]CVE Findings:[/bold yellow]")
                    for hit in result["cve_findings"]:
                        console.print(f"- {hit['name']} {hit['version']} -> {hit['cve']}: {hit['description']}")
                llm_summary = result.get("llm_summary")
                if not isinstance(llm_summary, str) or not llm_summary.strip():
                    llm_summary = "[No LLM summary returned]"
                console.print(Panel(llm_summary, title="🧠 LLM Summary", border_style="blue"))
                knowledge_context = result.get("knowledge_context")
                if isinstance(knowledge_context, str) and knowledge_context.strip():
                    console.print(
                        Panel(
                            knowledge_context,
                            title=" Operator Knowledge",
                            border_style="green",
                        )
                    )
                if result.get("errors"):
                    console.print(Panel(f"[yellow]Warnings: {result['errors']}[/yellow]", border_style="yellow"))
            else:
                console.print(Panel(f"[red]✗ Analysis failed: {result.get('errors')}[/red]", border_style="red"))
            input("\n[Press Enter to return to menu]")
            swoosh_transition()

        elif choice == "8":
            console.print("👋 Exiting Don Trabajo GPT. Hasta luego!", style="bold magenta")
            break

        else:
            console.print("⚠ Invalid choice. Try again.", style="bold red")
            input("\n[Press Enter to return to menu]")
            console.print(Panel("[green]Returning to menu...[/green]", border_style="bright_blue"))
            time.sleep(1)
            console.clear()


if __name__ == "__main__":
    main()

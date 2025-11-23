import os
import time
from rich.console import Console
from rich.panel import Panel
from don_trabajo_gpt_tui import show_main_menu
from cve_matcher import run_cve_matcher
from validate_tool_paths import validate_tool_paths
from animated_transition import animated_transition
from swoosh_transition import swoosh_transition
from linpeas_parser import parse_linpeas_output
from combo_linpeas_analyzer import analyze_linpeas_full_stack

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
            output_path = "sample_linpeas_output.json"
            from linpeas_preprocessor import preprocess_linpeas_output

            preprocess_linpeas_output(file_path, output_path)
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
            run_cve_matcher(file_path)
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
            try:
                from tools.oss_persona.tui_offline_llm import run as run_offline

                run_offline()
            except Exception as exc:
                console.print(f"[red]Offline LLM failed: {exc}[/red]")
            input("\n[Press Enter to return to menu]")
            swoosh_transition()

        elif choice == "7":
            file_path = _prompt_for_file("📄 Enter path to raw linPEAS .txt for full-stack analysis: ")
            if not file_path:
                continue
            animated_transition()
            analyze_linpeas_full_stack(file_path)
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

import os
import time
import json
from rich.console import Console
from rich.panel import Panel
from don_trabajo_gpt_tui import show_main_menu
from cve_matcher import run_cve_matcher
from validate_tool_paths import validate_tool_paths
from animated_transition import animated_transition
from swoosh_transition import swoosh_transition
from linpeas_parser import parse_linpeas_output

console = Console()

def main():
    while True:
        choice = show_main_menu()

        if choice == "0":
            file_path = input("🔧 Preprocess raw linPEAS .txt to JSON: ").strip()
            output_path = "sample_linpeas_output.json"
            from linpeas_preprocessor import preprocess_linpeas_output
            preprocess_linpeas_output(file_path, output_path)
            input("\n[Press Enter to return to menu]")
            swoosh_transition()

        elif choice == "1":
            file_path = input("📂 Enter path to linPEAS JSON output file: ").strip()
            if os.path.isfile(file_path):
                console.print("\a", end="")
                animated_transition()
                parse_linpeas_output(file_path)
                console.print("\a", style="green", end="")
                input("\n[Press Enter to return to menu]")
                swoosh_transition()
            else:
                console.print("\a", style="bold red", end="")
                console.print(f"❌ File not found: {file_path}", style="bold red")
                input("\n[Press Enter to return to menu]")
                console.print(Panel("[green]Returning to menu...[/green]", border_style="bright_blue"))
                time.sleep(1)
                console.clear()

        elif choice == "2":
            file_path = input("📂 Enter path to linPEAS JSON output file: ").strip()
            if os.path.isfile(file_path):
                console.print("\a", end="")
                animated_transition()
                run_cve_matcher(file_path)
                console.print("\a", style="green", end="")
                input("\n[Press Enter to return to menu]")
                swoosh_transition()
            else:
                console.print("\a", style="bold red", end="")
                console.print(f"❌ File not found: {file_path}", style="bold red")
                input("\n[Press Enter to return to menu]")
                console.print(Panel("[green]Returning to menu...[/green]", border_style="bright_blue"))
                time.sleep(1)
                console.clear()

        elif choice == "3":
            validate_tool_paths()
            console.print("\a", style="green", end="")
            input("\n[Press Enter to return to menu]")
            swoosh_transition()

        elif choice == "4":
            console.print("🧠 HTB Log Tracker is coming soon.", style="cyan")
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
            console.print("👋 Exiting Don Trabajo GPT. Hasta luego!", style="bold magenta")
            break

        else:
            console.print("❌ Invalid choice. Try again.", style="bold red")
            input("\n[Press Enter to return to menu]")
            console.print(Panel("[green]Returning to menu...[/green]", border_style="bright_blue"))
            time.sleep(1)
            console.clear()

if __name__ == "__main__":
    main()

import os
import time
from rich.console import Console
from rich.panel import Panel
from don_trabajo_gpt_tui import show_main_menu
from cve_matcher import run_cve_matcher
from validate_tool_paths import validate_tool_paths
from animated_transition import animated_transition
from swoosh_transition import swoosh_transition

console = Console()

def main():
    while True:
        choice = show_main_menu()

        if choice == "1":
            console.print("🔧 linPEAS Parser is under construction.", style="yellow")
            input("\n[Press Enter to return to menu]")
            console.print(Panel("[green]Returning to menu...[/green]", border_style="bright_blue"))
            time.sleep(1)
            console.clear()

        elif choice == "2":
            file_path = input("📂 Enter path to linPEAS JSON output file: ").strip()
            if os.path.isfile(file_path):
                console.print("\a", end="")         # terminal bell
                animated_transition()               # spinner-based animation
                run_cve_matcher(file_path)
                console.print("\a", style="green", end="")  # success beep
                input("\n[Press Enter to return to menu]")
                swoosh_transition()                 # swoosh up animation
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

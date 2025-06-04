from don_trabajo_gpt_tui import show_main_menu
from cve_matcher import run_cve_matcher
from validate_tool_paths import validate_paths
from don_trabajo_discord_bot import launch_discord_bot

def main():
    while True:
        choice = show_main_menu()
        if choice == "1":
            print("[*] linPEAS parsing not yet implemented.")
        elif choice == "2":
            run_cve_matcher()
        elif choice == "3":
            validate_paths()
        elif choice == "4":
            print("[*] HTB Log Tracker coming soon.")
        elif choice == "5":
            launch_discord_bot()
        elif choice == "6":
            print("Exiting Don Trabajo GPT. Hasta luego!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

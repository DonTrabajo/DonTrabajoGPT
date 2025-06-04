import json
from rich.console import Console

console = Console()

def run_cve_matcher(file_path="sample_linpeas_output.json"):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)

        if data.get("binaries"):
            console.print("\n🛡  [bold green]CVE Findings:[/bold green]")
            console.print("-" * 40)
            for binary in data["binaries"]:
                console.print(f"🔹 [bold]Binary:[/bold] {binary['name']} {binary['version']}")
                console.print(f"   [bold]CVE:[/bold] {binary['cve']}")
                console.print(f"   [bold]Description:[/bold] {binary['description']}\n")
        else:
            console.print("✅ No vulnerable binaries found in the JSON.", style="bold green")

    except FileNotFoundError:
        console.print(f"❌ Could not find file: {file_path}", style="bold red")
    except json.JSONDecodeError:
        console.print(f"❌ Failed to parse JSON from: {file_path}", style="bold red")

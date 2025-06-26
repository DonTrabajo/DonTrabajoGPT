import json
import re
from rich.console import Console
from rich.panel import Panel

console = Console()

def preprocess_linpeas_output(input_path, output_path):
    try:
        with open(input_path, "r") as f:
            raw = f.read()

        data = {}

        # Extract interesting users
        users_match = re.findall(r"^(\w+)\s+pts/\d+", raw, re.MULTILINE)
        data["interesting_users"] = list(set(users_match))

        # Extract SUID binaries
        suid_section = re.search(r"SUID.*?-{5,}\n(.*?)(?=\n\n|\Z)", raw, re.DOTALL | re.IGNORECASE)
        if suid_section:
            binaries = re.findall(r"(/[^\s]+)", suid_section.group(1))
            data["suid_binaries"] = list(set(binaries))
        else:
            data["suid_binaries"] = []

        # Extract kernel info
        kernel_info = re.search(r"Kernel.*?-{5,}\n(.*?)(?=\n\n|\Z)", raw, re.DOTALL | re.IGNORECASE)
        data["kernel_info"] = kernel_info.group(1).strip() if kernel_info else "Not found"

        # Extract IP addresses
        ip_matches = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", raw)
        data["ip_addresses"] = list(set(ip_matches))

        # Save to JSON
        with open(output_path, "w") as out:
            json.dump(data, out, indent=4)

        console.print(Panel(f"[green]✅ Preprocessing complete. Output saved to:[/green] [bold]{output_path}[/bold]", border_style="bright_green"))

    except FileNotFoundError:
        console.print(f"[red]❌ File not found: {input_path}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Error during preprocessing: {str(e)}[/red]")

# For direct CLI testing (optional)
if __name__ == "__main__":
    input_file = input("Enter path to raw linPEAS output (.txt): ").strip()
    output_file = "sample_linpeas_output.json"
    preprocess_linpeas_output(input_file, output_file)

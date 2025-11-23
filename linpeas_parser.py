
import json
from rich.console import Console
from rich.panel import Panel

console = Console()


def _validate_schema(data):
    meta = data.get("metadata", {})
    schema = meta.get("schema")
    if schema != "don-trabajo-linpeas-v1":
        console.print("[yellow]⚠ Unexpected schema version; results may be incomplete.[/yellow]")
    required = ["users", "suid_binaries", "kernel", "binaries"]
    missing = [k for k in required if k not in data]
    if missing:
        console.print(f"[yellow]⚠ Missing fields in JSON: {', '.join(missing)}[/yellow]")


def parse_linpeas_output(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        _validate_schema(data)

        console.print(Panel("[bold cyan]linPEAS Output Summary[/bold cyan]", border_style="bright_green"))

        users = data.get("users", [])
        if users:
            console.print("[bold yellow]Interesting Users:[/bold yellow]")
            for user in users:
                console.print(f"• {user}")

        suid_binaries = data.get("suid_binaries", [])
        if suid_binaries:
            console.print("\n[bold yellow]SUID Binaries:[/bold yellow]")
            for binary in suid_binaries:
                console.print(f"• {binary}")

        kernel = data.get("kernel", {})
        kernel_version = kernel.get("version", "unknown")
        kernel_raw = kernel.get("raw", "Not found")
        console.print("\n[bold yellow]Kernel Version:[/bold yellow]")
        console.print(f"{kernel_version} ({kernel_raw})")

        binaries = data.get("binaries", [])
        if binaries:
            console.print("\n[bold yellow]Binaries (parsed):[/bold yellow]")
            for b in binaries:
                console.print(f"• {b.get('name','unknown')} {b.get('version','unknown')}")

        if not any([users, suid_binaries, kernel, binaries]):
            console.print("[green]No high-interest data found (yet).[/green]")

    except FileNotFoundError:
        console.print(f"[red]✗ File not found: {file_path}[/red]")
    except json.JSONDecodeError:
        console.print(f"[red]✗ Invalid JSON format in: {file_path}[/red]")

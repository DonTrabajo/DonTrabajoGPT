from rich.console import Console
from rich.panel import Panel
import json

console = Console()


def summarize_linpeas_findings(parsed_data):
    console.print(Panel("[bold cyan]GPT Summary of linPEAS Findings[/bold cyan]", border_style="bright_blue"))

    users = parsed_data.get("users", [])
    if users:
        console.print("[bold yellow]👥 Users found on the system:[/bold yellow]")
        for user in users:
            console.print(f"- {user}")
        if "root" in users:
            console.print("[green]✓ Root user present. Check sudo permissions or root-owned binaries.[/green]")

    suids = parsed_data.get("suid_binaries", [])
    if suids:
        console.print("\n[bold yellow]🔒 SUID Binaries Detected:[/bold yellow]")
        for binary in suids:
            console.print(f"- {binary}")
        if any("/usr/bin/passwd" in s for s in suids):
            console.print("[green]→ Consider GTFOBins methods for SUID exploitation.[/green]")

    kernel = parsed_data.get("kernel", {})
    console.print("\n[bold yellow]🧠 Kernel Version:[/bold yellow]")
    console.print(kernel.get("raw", "Not found"))
    if "5.4" in kernel.get("raw", ""):
        console.print("[green]→ Possible privesc: overlayfs, dirtycow variants, etc.[/green]")

    ip_list = parsed_data.get("ip_addresses", [])
    if ip_list:
        console.print("\n[bold yellow]🌐 IPs Discovered:[/bold yellow]")
        for ip in ip_list:
            console.print(f"- {ip}")

    bins = parsed_data.get("binaries", [])
    if bins:
        console.print("\n[bold yellow]📦 Parsed Binaries:[/bold yellow]")
        for b in bins:
            console.print(f"- {b.get('name','unknown')} {b.get('version','unknown')}")

    if not users and not suids and not kernel:
        console.print("[dim]No significant findings from linPEAS output.[/dim]")


if __name__ == "__main__":
    path = input("Enter path to parsed linPEAS JSON: ").strip()
    with open(path, "r") as f:
        data = json.load(f)
    summarize_linpeas_findings(data)

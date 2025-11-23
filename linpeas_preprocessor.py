import json
import re
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()


def _extract_users(raw: str):
    return sorted(set(re.findall(r"^([\w<>-]+)\s+pts/\d+", raw, re.MULTILINE)))


def _extract_suid(raw: str):
    suid_section = re.search(r"SUID.*?-{5,}\n(.*?)(?=\n\n|\Z)", raw, re.DOTALL | re.IGNORECASE)
    if not suid_section:
        return []
    return sorted(set(re.findall(r"(/[^\s]+)", suid_section.group(1))))


def _extract_kernel(raw: str):
    kernel_section = re.search(r"Kernel.*?-{5,}\n(.*?)(?=\n\n|\Z)", raw, re.DOTALL | re.IGNORECASE)
    if not kernel_section:
        kernel_section = re.search(r"Linux version ([^\n]+)", raw, re.IGNORECASE)
    text = kernel_section.group(1).strip() if kernel_section else ""
    version_match = re.search(r"(\d+\.\d+\.\d+(?:-\d+)?)", text)
    return {"raw": text or "Not found", "version": version_match.group(1) if version_match else "unknown"}


def _extract_ips(raw: str):
    ips = set(re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", raw))
    if "<LAB_IP>" in raw:
        ips.add("<LAB_IP>")
    return sorted(ips)


def _extract_binaries(raw: str, suids):
    """
    Light-weight binary discovery:
    - pull binary names from SUID entries
    - scan for '<name> version X.Y' patterns
    - capture daemons from 'pid/name' tokens
    """
    binaries = []
    seen = set()

    def add_binary(name, version="unknown"):
        key = (name.lower(), version)
        if key in seen:
            return
        binaries.append({"name": name, "version": version})
        seen.add(key)

    # from SUID paths
    for path in suids:
        name = Path(path).name
        add_binary(name)

    # "name version 1.2.3"
    for m in re.finditer(r"([A-Za-z0-9._+-]+)\s+version\s+([0-9][\w.\-]*)", raw, re.IGNORECASE):
        add_binary(m.group(1), m.group(2))

    # processes like "1234/sshd"
    for m in re.finditer(r"\d+/([A-Za-z0-9._+-]+)", raw):
        add_binary(m.group(1))

    return binaries


def preprocess_linpeas_output(input_path, output_path):
    try:
        with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
            raw = f.read()

        users = _extract_users(raw)
        suids = _extract_suid(raw)
        kernel = _extract_kernel(raw)
        ips = _extract_ips(raw)
        binaries = _extract_binaries(raw, suids)

        data = {
            "metadata": {
                "source": str(input_path),
                "schema": "don-trabajo-linpeas-v1",
            },
            "users": users,
            "suid_binaries": suids,
            "kernel": kernel,
            "ip_addresses": ips,
            "binaries": binaries,
        }

        with open(output_path, "w", encoding="utf-8") as out:
            json.dump(data, out, indent=4)

        console.print(
            Panel(
                f"[green]✓ Preprocessing complete. Output saved to:[/green] [bold]{output_path}[/bold]",
                border_style="bright_green",
            )
        )

    except FileNotFoundError:
        console.print(f"[red]✗ File not found: {input_path}[/red]")
    except Exception as e:
        console.print(f"[red]✗ Error during preprocessing: {str(e)}[/red]")


if __name__ == "__main__":
    input_file = input("Enter path to raw linPEAS output (.txt): ").strip()
    output_file = "sample_linpeas_output.json"
    preprocess_linpeas_output(input_file, output_file)

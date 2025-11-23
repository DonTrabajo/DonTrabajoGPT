import json
from rich.console import Console

console = Console()

# Minimal static CVE hints for demo purposes.
CVE_DB = {
    "sudo": [
        {"version_substr": "1.8", "cve": "CVE-2021-3156", "description": "Sudo Baron Samedit heap overflow"},
    ],
    "passwd": [
        {"version_substr": "", "cve": "CVE-2019-6109", "description": "Potential OpenSSH scp path injection (check version)"},
    ],
    "sshd": [
        {"version_substr": "8.2", "cve": "CVE-2020-14145", "description": "Potential timing issue in OpenSSH 8.2"},
    ],
}


def _match_cves(binaries):
    findings = []
    for binary in binaries:
        name = (binary.get("name") or "").lower()
        version = binary.get("version") or ""
        if not name:
            continue
        for cand in CVE_DB.get(name, []):
            ver_sub = cand["version_substr"]
            if not ver_sub or ver_sub in version:
                findings.append(
                    {
                        "name": binary.get("name", ""),
                        "version": version or "unknown",
                        "cve": cand["cve"],
                        "description": cand["description"],
                    }
                )
    return findings


def run_cve_matcher(file_path="sample_linpeas_output.json"):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        binaries = data.get("binaries", [])
        matches = _match_cves(binaries)

        if matches:
            console.print("\n✅  [bold green]CVE Findings:[/bold green]")
            console.print("-" * 40)
            for hit in matches:
                console.print(f"• [bold]{hit['name']}[/bold] {hit['version']}")
                console.print(f"   CVE: {hit['cve']}")
                console.print(f"   Desc: {hit['description']}\n")
        else:
            console.print("ℹ No vulnerable binaries found in the JSON.", style="bold green")

    except FileNotFoundError:
        console.print(f"✗ Could not find file: {file_path}", style="bold red")
    except json.JSONDecodeError:
        console.print(f"✗ Failed to parse JSON from: {file_path}", style="bold red")

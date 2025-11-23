import json
from rich.console import Console

console = Console()

# Minimal static CVE hints for demo purposes.
# Structure: name -> list of {min_version, max_version, cve, description}
CVE_DB = {
    "sudo": [
        {"min_version": "1.8.0", "max_version": "1.9.5p2", "cve": "CVE-2021-3156", "description": "Sudo Baron Samedit heap overflow"},
    ],
    "sshd": [
        {"min_version": "8.2", "max_version": "8.2", "cve": "CVE-2020-14145", "description": "OpenSSH timing issue in 8.2"},
    ],
}


def _ver_tuple(ver: str):
    try:
        return tuple(int(x) for x in ver.split(".") if x.isdigit())
    except Exception:
        return ()


def _version_in_range(version: str, min_v: str, max_v: str):
    vt = _ver_tuple(version)
    min_t = _ver_tuple(min_v) if min_v else ()
    max_t = _ver_tuple(max_v) if max_v else ()
    if min_t and vt and vt < min_t:
        return False
    if max_t and vt and vt > max_t:
        return False
    return True


def _match_cves(binaries):
    findings = []
    for binary in binaries:
        name = (binary.get("name") or "").lower()
        version = binary.get("version") or ""
        if not name:
            continue
        for cand in CVE_DB.get(name, []):
            if _version_in_range(version, cand.get("min_version",""), cand.get("max_version","")):
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

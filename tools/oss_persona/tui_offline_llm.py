import os, glob, datetime as dt
from pathlib import Path
from textwrap import dedent
from rich.console import Console
from rich.panel import Panel
try:
    from dotenv import load_dotenv; load_dotenv()
except Exception:
    pass

from .offline_llm_client import chat

console = Console()

def _env(k, d=None):
    v = os.getenv(k)
    return v if v not in (None,"","None") else d

def _load_latest_artifact():
    artifacts_dir = Path(_env("ARTIFACTS_DIR","artifacts"))
    patterns = [p.strip() for p in _env("ARTIFACT_PATTERNS","linpeas*.json,findings*.json,*.txt").split(",")]
    candidates = []
    for pat in patterns:
        candidates += [Path(p) for p in glob.glob(str(artifacts_dir / pat))]
    if not candidates: return None
    latest = max(candidates, key=lambda p: p.stat().st_mtime)
    return latest.read_text(encoding="utf-8", errors="ignore")

def run():
    findings = _load_latest_artifact()
    if not findings:
        console.print("[yellow]No artifacts found in $ARTIFACTS_DIR; paste text then Enter.[/]")
        findings = console.input("> ")

    sys_path = _env("DONTRABAJO_SYSTEM","tools/oss_persona/persona_prompt.txt")
    system = Path(sys_path).read_text(encoding="utf-8", errors="ignore") if Path(sys_path).exists() \
             else "You are DonTrabajoGPT offline. Be concise, OPSEC-safe, and practical."

    prompt = dedent(f"""
    Summarize the following findings for an internal target ONLY.
    Provide: (1) 5–10 bullet summary (2) Ordered next steps (3) Concrete commands for local lab targets (no real domains).
    Findings:
    {findings[:35000]}
    """).strip()

    out = chat([{"role":"system","content":system},{"role":"user","content":prompt}], temperature=0.2)
    console.print(Panel(out, title="Local LLM (offline) output"))
    notes = Path(_env("NOTES_DIR","notes")); notes.mkdir(parents=True, exist_ok=True)
    out_path = notes / f"ai_summary_{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    out_path.write_text(out, encoding="utf-8")
    console.print(f"[green]Saved → {out_path}[/]")

if __name__ == "__main__":
    run()

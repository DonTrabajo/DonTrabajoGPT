from pathlib import Path

def load_persona_text(path: str | None) -> str:
    if not path:
        return ""
    p = Path(path).expanduser()
    if not p.exists():
        return ""
    try:
        return p.read_text(encoding="utf-8").strip()
    except Exception:
        return ""

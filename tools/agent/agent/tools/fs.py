from pathlib import Path

def fs_read(path: str):
    p = Path(path).expanduser().resolve()
    return {"path": str(p), "text": p.read_text(encoding="utf-8")}

def fs_write(path: str, text: str):
    p = Path(path).expanduser().resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return {"path": str(p), "bytes": len(text.encode('utf-8'))}

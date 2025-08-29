import subprocess, shlex

_BLOCKED = {"rm", "shutdown", "reboot", "mkfs", "mount", "umount", "dd"}

def sh_run(cmd: str):
    parts = shlex.split(cmd)
    if parts and parts[0] in _BLOCKED:
        return {"error": f"blocked command: {parts[0]}"}
    try:
        out = subprocess.run(parts, capture_output=True, text=True, timeout=20)
        return {"stdout": out.stdout, "stderr": out.stderr, "returncode": out.returncode}
    except Exception as e:
        return {"error": str(e)}

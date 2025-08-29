import subprocess, tempfile, textwrap, sys, os

def py_exec(code: str):
    """Run a short Python snippet in a separate process with -I for isolation.
    Returns stdout/stderr. Not a real sandbox; be careful!"""
    code = textwrap.dedent(code)
    with tempfile.TemporaryDirectory() as td:
        pyfile = os.path.join(td, "snippet.py")
        with open(pyfile, "w", encoding="utf-8") as f:
            f.write(code)
        proc = subprocess.run(
            [sys.executable, "-I", pyfile],
            capture_output=True, text=True, timeout=20
        )
        return {"stdout": proc.stdout, "stderr": proc.stderr, "returncode": proc.returncode}

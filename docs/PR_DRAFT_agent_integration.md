## feat(agent): local OSS agent (browse/tools/code-exec) + Don Trabajo persona

### Summary
This PR adds an **offline-first agent** under `tools/agent/` that equips DonTrabajoGPT with:
- Web search + page extraction (DuckDuckGo + trafilatura)
- Tool calling protocol (JSON in ```tool fences)
- Local Python code execution in an isolated subprocess
- Optional filesystem read/write tools
- Optional shell runner (disabled by default)
- Persona hook via `PERSONA_FILE` (Don Trabajo system addendum included)

### Why
- Keep sensitive recon data local; only fetch web content when necessary.
- Reuse the agent for recon automation, OSINT, CVE triage, and quick scripts.

### How to Run
```
pip install -r tools/agent/requirements-agent.txt
cp tools/agent/.env.example tools/agent/.env
# optionally enable persona:
echo "PERSONA_FILE=personas/don_trabajo/persona.md" >> tools/agent/.env
python -m tools.agent.runner repl
```

### Safety
- `ENABLE_SHELL=false` by default.
- `SHOW_CHAIN_OF_THOUGHT=false` by default.

### Next
- Add a TUI entry to launch the agent REPL.
- Add a recon tool wrapper to call linPEAS/Nmap parsers from within the agent.

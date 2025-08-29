# DonTrabajoGPT: Local OSS Agent Integration

This adds a **local-first agent** (browsing + tool use + code execution + optional chain-of-thought) inside your repo under `tools/agent/`, plus a **Don Trabajo persona wrapper**.

## Layout
```
tools/
  agent/
    __init__.py
    runner.py                 # `python -m tools.agent.runner repl`
    agent/                    # core agent package
      __init__.py
      chain.py
      model.py
      prompts.py
      schema.py
      persona_loader.py
      tools/
        __init__.py
        web.py
        python_exec.py
        fs.py
        shell.py
    requirements-agent.txt
    .env.example
personas/
  don_trabajo/
    persona.md
    system_overrides.md
docs/
  PR_DRAFT_agent_integration.md
scripts/
  agent_install.sh
```

## Quickstart
```bash
# From repo root
python -m venv .venv && source .venv/bin/activate
pip install -r tools/agent/requirements-agent.txt

# Copy environment example
cp tools/agent/.env.example tools/agent/.env

# (Optional) Point to Don Trabajo persona prompt
# This file is used when PERSONA_FILE is set (see .env.example).
echo "PERSONA_FILE=personas/don_trabajo/persona.md" >> tools/agent/.env

# Run REPL
python -m tools.agent.runner repl
# Or one-shot
python -m tools.agent.runner chat "Find three recent cyber cons in Seattle and summarize themes."
```

## Add a TUI Menu Entry (optional)
In `don_trabajo_gpt.py` or `don_trabajo_gpt_tui.py`, add an item like:
```python
elif choice == "7":
    os.system("python -m tools.agent.runner repl")
```
_(Ensure the venv is active.)_

## Safe defaults
- `ENABLE_SHELL=false` by default.
- `SHOW_CHAIN_OF_THOUGHT=false` by default (toggle for local debugging only).

## Git flow
```bash
git checkout -b feat/oss-agent
# unzip contents at repo root
git add tools/agent personas/don_trabajo scripts/agent_install.sh README_AGENT.md docs/PR_DRAFT_agent_integration.md
git commit -m "feat(agent): add local OSS agent (browse/tools/code-exec) + Don Trabajo persona"
git push origin feat/oss-agent
# open PR using the draft in docs/PR_DRAFT_agent_integration.md
```

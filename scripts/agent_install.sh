#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
repo_root="$(cd "$here/.." && pwd)"
python -m venv "$repo_root/.venv"
source "$repo_root/.venv/bin/activate"
pip install -r "$repo_root/tools/agent/requirements-agent.txt"
cp -n "$repo_root/tools/agent/.env.example" "$repo_root/tools/agent/.env" || true
echo "Done. Edit tools/agent/.env and run: python -m tools.agent.runner repl"

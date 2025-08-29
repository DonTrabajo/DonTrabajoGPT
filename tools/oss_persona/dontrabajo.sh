#!/usr/bin/env bash
set -euo pipefail
MODEL_TAG="${OSS_MODEL:-gpt-oss:20b}"
WRAPPER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WRAPPER_PY="$WRAPPER_DIR/don_trabajo_oss.py"
OLLAMA_HOST="${OLLAMA_HOST:-http://localhost:11434}"
AUTO_PULL="${AUTO_PULL:-1}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

command -v ollama >/dev/null 2>&1 || { echo "❌ Ollama not found: https://ollama.com"; exit 1; }

if ! curl -sSf "$OLLAMA_HOST/api/tags" >/dev/null 2>&1; then
  echo "➜ Starting Ollama..."
  if launchctl list | grep -q "io.ollama"; then
    launchctl start io.ollama || true
  else
    nohup ollama serve >/tmp/ollama-serve.log 2>&1 &
  fi
  for i in {1..20}; do
    curl -sSf "$OLLAMA_HOST/api/tags" >/dev/null 2>&1 && break
    sleep 0.5
  done
  curl -sSf "$OLLAMA_HOST/api/tags" >/dev/null 2>&1 || { echo "❌ Could not reach $OLLAMA_HOST"; exit 1; }
fi

if [[ "$AUTO_PULL" == "1" ]]; then
  if ! ollama list | awk '{print $1}' | grep -qx "$MODEL_TAG"; then
    echo "➜ Pulling $MODEL_TAG (one-time)…"
    ollama pull "$MODEL_TAG"
  fi
fi

[[ -f "$WRAPPER_PY" ]] || { echo "❌ Wrapper not found: $WRAPPER_PY"; exit 1; }
command -v "$PYTHON_BIN" >/dev/null 2>&1 || { echo "❌ $PYTHON_BIN not found"; exit 1; }

echo "🔥 Launching Don Trabajo GPT on $MODEL_TAG via $OLLAMA_HOST"
exec "$PYTHON_BIN" "$WRAPPER_PY"

# Don Trabajo OSS Persona (Ollama + gpt-oss:20b)

Local persona wrapper for DonTrabajoGPT using **gpt-oss:20b** via **Ollama**.

## Quickstart

    # One-time: pull weights
    ollama pull gpt-oss:20b

    # Install Python deps
    python3 -m pip install -r tools/oss_persona/requirements.txt

    # Launch persona chat
    tools/oss_persona/dontrabajo.sh

## Env Vars
- OSS_MODEL (default: gpt-oss:20b)
- OLLAMA_HOST (default: http://localhost:11434)
- AUTO_PULL (default: 1)
- PYTHON_BIN (default: python3)
- OSS_TEMPERATURE, OSS_NUM_CTX (tuning options)

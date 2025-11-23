# Don Trabajo GPT 🤖💀

> A GPT-powered, terminal-native hacking assistant for offensive security labs, red teams, and cyberpunk operators — now with **Offline-First** superpowers.

[![MIT License](https://img.shields.io/github/license/DonTrabajo/DonTrabajoGPT)](LICENSE)  
[![Last Commit](https://img.shields.io/github/last-commit/DonTrabajo/DonTrabajoGPT)](https://github.com/DonTrabajo/DonTrabajoGPT/commits/main)  
[![Languages](https://img.shields.io/github/languages/top/DonTrabajo/DonTrabajoGPT)](https://github.com/DonTrabajo/DonTrabajoGPT)  
[![Stars](https://img.shields.io/github/stars/DonTrabajo/DonTrabajoGPT?style=social)](https://github.com/DonTrabajo/DonTrabajoGPT/stargazers)

---

## 🎯 Purpose

**Don Trabajo GPT** is a lightweight, terminal-native AI assistant that augments red-team ops and offensive-security workflows. It parses **linPEAS**, matches **CVEs**, validates toolchains, and—when you need it—spins up a **fully local LLM** to summarize findings and draft next steps with **zero** cloud calls. Your data stays where it belongs: on your machine.

---

## ✨ Core Features

- **linPEAS pipeline**: preprocess → parse → triage  
- **CVE matcher**: extract and rank potential issues from JSON  
- **Tool path validation**: sanity-check required binaries  
- **Local LLM (Offline-First)**: summarize findings & generate next steps via **Ollama** (OpenAI-compatible, 100% local)  
- **Clean TUI**: Rich-powered CLI with color, panels, and smooth UX  
- **Demo-ready**: Copy/paste quick starts + smoke tests for talks

---

## 📸 Screenshots & Terminal Preview

```
╭────────────────────────────╮
│ Don Trabajo GPT            │
│ CyberOps Console Interface │
╰────────────────────────────╯
???????????????????????????????????????????????????????????
? Option   ? Feature                        ? Status       ?
???????????????????????????????????????????????????????????
і 0        і Preprocess linPEAS Raw Output  і 🆕            і
і 1        і Parse linPEAS Output           і ✅ Ready      і
і 2        і Run CVE Matcher                і ✅ Ready      і
і 3        і Tool Path Validation           і ✅ Ready      і
і 4        і HTB Log Tracker                і Coming Soon  і
і 5        і Launch Discord Bot             і Coming Soon  і
і 6        і Offline LLM (Local Persona)    і Beta         і
і 7        і Full linPEAS Analyzer (combo)  і Beta         і
і 8        і Exit                           і              і
АДДДДДДДДДДБДДДДДДДДДДДДДДДДДДДДДДДДДДДДДДДДБДДДДДДДДДДДДДДЩ
Choose an option [0/1/2/3/4/5/6/7/8]:
```

---

## 🚀 Quick Start

```bash
# Clone the repo and enter the folder
git clone https://github.com/DonTrabajo/DonTrabajoGPT.git
cd DonTrabajoGPT

# Create & activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Validate your tool paths
python validate_tool_paths.py

# Launch the assistant (TUI)
python don_trabajo_gpt.py
```

---

## 🔒 Offline-First Mode (Local LLM)

Run DonTrabajoGPT with a **fully local brain** using [Ollama](https://ollama.ai). No Internet calls; everything stays on your box.

```bash
# 1) Install & start Ollama (macOS)
brew install --cask ollama
ollama serve    # ensures 127.0.0.1:11434 is listening

# 2) Pick a local model you already have (examples)
ollama list
#   deepseek-r1:8b         # lighter/faster
#   gpt-oss:20b            # bigger brain, needs RAM

# 3) Configure DonTrabajoGPT
cp .env.example .env
# In .env set at minimum:
#   OPENAI_BASE_URL=http://127.0.0.1:11434/v1
#   OPENAI_API_KEY=ollama
#   LLM_MODEL=deepseek-r1:8b   # or gpt-oss:20b
```

**Summarize findings (offline):**
```bash
mkdir -p artifacts notes
cp sample_linpeas_output.json artifacts/        # demo artifact
python -m tools.oss_persona.tui_offline_llm     # writes notes/ai_summary_YYYYMMDD-HHMMSS.md
```

**Smoke test (OpenAI-compatible client → Ollama):**
```bash
python - <<'PY'
from openai import OpenAI
c = OpenAI(base_url="http://127.0.0.1:11434/v1", api_key="ollama")
print([m.id for m in c.models.list().data])
PY
```

> **What stays local:** the LLM, prompts, artifacts, mirrors, and notes.  
> **What leaves the laptop:** nothing—unless you explicitly connect to a client network for testing.

---

## 🎛️ 5-Minute Demo Recipe (Conference-friendly)

1. Prove no cloud calls:  
   `curl -s http://127.0.0.1:11434/v1/models` ✅  
2. Put a sample artifact in `artifacts/` (or paste on prompt).  
3. **TUI → Option 6**: Local LLM (offline) summary → generate checklist & next steps.  
4. Show the saved Markdown in `notes/`.  
5. (Optional) Toggle Wi-Fi off and repeat. Still works.

---

## 📋 Usage Examples

### Run the TUI
```bash
python don_trabajo_gpt.py
```
Choose options by number:  
- **0** - Preprocess linPEAS raw output  
- **1** - Parse linPEAS JSON output  
- **2** - Match CVEs from linPEAS results  
- **3** - Validate `tool_paths.json`  
- **4** - HTB Log Tracker *(coming soon)*  
- **5** - Discord bot *(coming soon)*  
- **6** - **Local LLM (Offline)**: summarize findings & draft next steps  
- **7** - Full linPEAS analyzer (preprocess → parse → CVE → GPT)  
- **8** - Exit  

### Validate Tool Paths
```bash
python validate_tool_paths.py
# ✅ nmap: /usr/bin/nmap
# ❌ enum4linux: /usr/local/bin/enum4linux
```

### CVE Matcher
```bash
python don_trabajo_gpt.py
# Choose 2 → point to your linPEAS JSON → get ranked findings.
```

### Local LLM (standalone)
```bash
# Uses .env to hit your local Ollama model
python -m tools.oss_persona.tui_offline_llm
```

---

## 🗂️ Directory Layout

```
DonTrabajoGPT/
|- animated_transition.py
|- cve_matcher.py
|- docs/
|  |- CNAME
|  |- index.html
|- don_trabajo_gpt.py              # Main TUI launcher
|- don_trabajo_gpt_tui.py          # Rich-powered menu UI
|- requirements.txt
|- sample_linpeas_output.json
|- swoosh_transition.py
|- tools/
|  |- oss_persona/
|     |- persona_prompt.txt        # system prompt for local persona
|     |- oss_client.py             # OpenAI-compatible (Ollama) client
|     |- tui_offline_llm.py        # Offline summary runner
|- validate_tool_paths.py
|- .env.example                    # Offline-first config template
|- artifacts/                      # (gitignored) analysis inputs
|- notes/                          # (gitignored) generated summaries
|- LICENSE
|- README.md
```

---

## 🧠 Roadmap

| Status     | Feature                                                   |
|------------|-----------------------------------------------------------|
| ✅ Ready   | linPEAS preprocess/parse                                  |
| ✅ Ready   | CVE matcher (JSON)                                        |
| ✅ Ready   | Tool path validation                                      |
| ✅ Ready   | **Local LLM (Offline-First)** via Ollama                  |
| 🔄 WIP     | HTB Log Tracker                                           |
| 🔄 WIP     | Discord Bot (ops logging & notifications)                 |
| ⏳ Planned | Enum4linux / WinPEAS analyzers                            |
| ⏳ Planned | Report export (Markdown/HTML one-pager)                   |
| ⏳ Planned | Plugin system for analyzers (drop-in modules)             |
| ⏳ Planned | Docs site revamp (screenshots, offline demo walkthrough)  |

---

## ⚙️ Configuration (.env)

Copy and tweak:

```env
# === Offline LLM defaults (Ollama) ===
LOCAL_LLM=true
OPENAI_BASE_URL=http://127.0.0.1:11434/v1
OPENAI_API_KEY=ollama
LLM_MODEL=deepseek-r1:8b        # or gpt-oss:20b

# Optional local RAG sidecar (leave empty if not using)
RAG_URL=

# Persona/system prompt
DONTRABAJO_SYSTEM=tools/oss_persona/persona_prompt.txt

# Where to read findings (for summaries)
ARTIFACTS_DIR=artifacts
ARTIFACT_PATTERNS=linpeas*.json,findings*.json,*.txt

# Where to save AI summaries
NOTES_DIR=notes
```

---

## 🧪 Dev Tips

- Use a Python venv (`.venv`) and keep `artifacts/` & `notes/` out of git (already ignored).  
- For talks, prep a `notes/` wipe and an `artifacts/` seed file to reset in seconds.  
- Want a `Makefile`?  
  - `make offline-demo` → env + sample artifact + run Option 6  
  - `make clean-notes` → empty `notes/`

---

## 👤 About the Author

**Don Trabajo** — cybersecurity operator, hacker-artist, and creative force behind **Prox Offensive**. Fusing tech with spirit, code with culture, **Don Trabajo GPT** is where tools meet intuition.

> *“Enumeration is half the battle. The other half is naming your tools something dope.”*  
> — Don Trabajo

---

## 📜 License

This project is licensed under the **MIT License**. See [LICENSE](./LICENSE) for details.

---


**¡Adelante siempre!**  
*Less heroics. More reliability. Keep the receipts.*









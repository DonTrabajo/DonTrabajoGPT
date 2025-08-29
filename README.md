# Don Trabajo GPT 🤖💀

> A GPT-powered, terminal-native hacking assistant for offensive security labs, red teams, and cyberpunk operators.

[![MIT License](https://img.shields.io/github/license/DonTrabajo/DonTrabajoGPT)](LICENSE)  
[![Last Commit](https://img.shields.io/github/last-commit/DonTrabajo/DonTrabajoGPT)](https://github.com/DonTrabajo/DonTrabajoGPT/commits/main)  
[![Languages](https://img.shields.io/github/languages/top/DonTrabajo/DonTrabajoGPT)](https://github.com/DonTrabajo/DonTrabajoGPT)  
[![Stars](https://img.shields.io/github/stars/DonTrabajo/DonTrabajoGPT?style=social)](https://github.com/DonTrabajo/DonTrabajoGPT/stargazers)  

---

## 🎯 Purpose

Don Trabajo GPT is a lightweight, terminal-native AI assistant built to augment red-team operations and offensive-security workflows. From parsing linPEAS output to matching CVEs and launching Discord logs, it’s your on-demand cyberpunk field agent.

---

## 📸 Screenshots & Terminal Preview

```
╭────────────────────────────╮
│ Don Trabajo GPT            │
│ CyberOps Console Interface │
╰────────────────────────────╯
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Option   ┃ Feature                       ┃ Status      ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ 0        │ Preprocess linPEAS Raw Output │ 🔥 New      │
│ 1        │ Parse linPEAS Output          │ ✅ Ready    │
│ 2        │ Run CVE Matcher               │ ✅ Ready    │
│ 3        │ Tool Path Validation          │ ✅ Ready    │
│ 4        │ HTB Log Tracker               │ Coming Soon │
│ 5        │ Launch Discord Bot            │ Coming Soon │
│ 6        │ Exit                          │             │
└──────────┴───────────────────────────────┴─────────────┘
Choose an option [0/1/2/3/4/5/6]:
```

---

## 🚀 Quick Start

```bash
# Clone the repo and enter the folder
git clone https://github.com/DonTrabajo/DonTrabajoGPT.git
cd DonTrabajoGPT

# Create & activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Validate your tool paths
python validate_tool_paths.py

# Launch the assistant
python don_trabajo_gpt.py
```

---

## 📋 Usage Examples

### 1. Run the TUI
```bash
$ python don_trabajo_gpt.py
```
Choose options by number, e.g.:
- **0** – Preprocess linPEAS raw output
- **1** – Parse linPEAS JSON output
- **2** – Match CVEs from linPEAS results
- **3** – Validate `tool_paths.json`
- **4** – HTB Log Tracker (coming soon)
- **5** – Launch Discord bot (coming soon)
- **6** – Exit

### 2. Validate Tool Paths
```bash
$ python validate_tool_paths.py
✅ nmap: /usr/bin/nmap
❌ enum4linux: /usr/local/bin/enum4linux
...
```

### 3. Run CVE Matcher
```bash
$ python don_trabajo_gpt.py
Choose an option [0/1/2/3/4/5/6]: 2
📂 Enter path to linPEAS JSON output file: path/to/linpeas.json
🛡  CVE Findings:
...  # paged output
Press [Enter] to return to menu.
```

### 4. Launch Discord Bot (Future)
```bash
$ python don_trabajo_discord_bot.py
```
*(Requires configuration: insert your Discord token & channel ID.)*

---

## 📁 Directory Layout

```
DonTrabajoGPT/
├── animated_transition.py      # Spinner & loading animations
├── cve_matcher.py              # CVE matching logic (reads any JSON)
├── docs/                       # GitHub Pages landing site
│   ├── CNAME
│   └── index.html
├── don_trabajo_gpt.py          # Main TUI launcher script
├── don_trabajo_gpt_tui.py      # Rich-powered menu UI
├── don_trabajo_discord_bot.py  # Discord logging integration
├── ping.wav                    # (Optional) Ping sound for notifications
├── requirements.txt            # pip install -r requirements.txt
├── sample_linpeas_output.json  # Dummy JSON for CVE matcher tests
├── swoosh_transition.py        # “Swoosh” screen transition animation
├── validate_tool_paths.py      # Check required tool executables
├── README.md                   # This file
├── LICENSE                     # MIT License
├── .gitignore
└── venv/                       # Python virtual environment
```

---

## 🧠 Roadmap

| Status     | Feature                                              |
|------------|------------------------------------------------------|
| ✅ Ready   | Run CVE Matcher on any linPEAS JSON                  |
| ✅ Ready   | Tool Path Validation via `tool_paths.json`           |
| ✅ Ready   | Parse linPEAS Output                                 |
| 🔄 WIP     | Discord Bot (logging & notifications)                |
| 🔄 WIP     | HTB Log Tracker (record per-machine progress)        |
| ⏳ Planned | Enum4linux Parser                                    |
| ⏳ Planned | Windows PEAS Support                                 |
| ⏳ Planned | GitHub Pages–hosted docs & landing page              |
| ⏳ Planned | Custom CVE DB integration                            |
| ⏳ Planned | Terminal-UI enhancements (colors, trees, animations) |

---

## 👤 About the Author

**Don Trabajo** is a cybersecurity operator, hacker-artist, and creative force behind [Prox Offensive Information Security](https://github.com/DonTrabajo). Fusing tech with spirit, code with culture, Don Trabajo GPT is the manifestation of tools meeting intuition.

> *“Enumeration is half the battle. The other half is naming your tools something dope.”*  
> _– Don Trabajo_

---

## 📜 License

This project is licensed under the **MIT License**. See [LICENSE](./LICENSE) for details.

---

**¡Adelante siempre!**
---

## DonTrabajo OSS Persona & Local Agent

- **Persona wrapper & CLI:** see [`tools/oss_persona/README.md`](tools/oss_persona/README.md)  
- **Local agent quickstart:** see [`README_AGENT.md`](README_AGENT.md)  
- **Integration notes / PR draft:** see [`docs/PR_DRAFT_agent_integration.md`](docs/PR_DRAFT_agent_integration.md)

> Heads-up: the agent’s web search is still evolving (soft-404 filtering, reranker heuristics). Expect rough edges in `tools/agent/` while it’s marked WIP.

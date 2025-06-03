# Don Trabajo GPT 🤖💀

> A GPT-powered, terminal-native hacking assistant for offensive security labs, red teams, and cyberpunk operators.

[![MIT License](https://img.shields.io/github/license/DonTrabajo/DonTrabajoGPT)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/DonTrabajo/DonTrabajoGPT)](https://github.com/DonTrabajo/DonTrabajoGPT/commits/main)
[![Languages](https://img.shields.io/github/languages/top/DonTrabajo/DonTrabajoGPT)](https://github.com/DonTrabajo/DonTrabajoGPT)
[![Stars](https://img.shields.io/github/stars/DonTrabajo/DonTrabajoGPT?style=social)](https://github.com/DonTrabajo/DonTrabajoGPT/stargazers)

---

## 🎯 Purpose

Don Trabajo GPT is a lightweight, terminal-native AI assistant designed to augment red team operations and offensive security workflows. From parsing recon data to suggesting CVEs and building reports, it’s your on-demand cyberpunk field agent.

---

## 🛠️ Features
- Interactive CLI with menu system
- Nmap output parsing and command suggestion
- linPEAS output parser
- Offline CVE matcher module
- Markdown reporting per HTB machine
- Tool path customization via `tool_paths.json`
- Real-time Discord bot logging

---

## 🚀 Quick Start

```bash
# Clone and enter
$ git clone https://github.com/DonTrabajo/DonTrabajoGPT.git
$ cd DonTrabajoGPT

# Validate your tool paths
$ python validate_tool_paths.py

# Launch the assistant
$ python don_trabajo_gpt.py
```

---

## 📸 Example Usage
```bash
Welcome to Don Trabajo GPT
1. Analyze Nmap output
2. Parse linPEAS output
3. Search Offline CVEs from Nmap
4. Exit
```

---

## 📂 Directory Layout
```
DonTrabajoGPT/
├── don_trabajo_gpt.py
├── validate_tool_paths.py
├── cve_matcher.py
├── don_trabajo_discord_bot.py
├── tool_paths.json
├── HTB/                       # Auto-generated machine folders
├── README.md
├── LICENSE
├── .gitignore
```

---

## 🧠 Roadmap

- [x] Nmap + linPEAS parsing
- [x] CVE matcher with offline DB
- [x] Custom tool path config
- [x] Discord logging bot
- [ ] Enum4linux parser
- [ ] winPEAS support
- [ ] Discord AI replies
- [ ] GitHub Pages site

---

## 👤 About the Author

**Don Trabajo** is a cybersecurity operator, hacker-artist, and creative force behind [Prox Offensive Information Security](https://github.com/DonTrabajo). Fusing tech with spirit, code with culture, Don Trabajo GPT is the manifestation of tools meeting intuition.

> *"Enumeration is half the battle. The other half is naming your tools something dope."*

---

## 📜 License

MIT License. See [LICENSE](./LICENSE).

---

**¡Adelante siempre!**
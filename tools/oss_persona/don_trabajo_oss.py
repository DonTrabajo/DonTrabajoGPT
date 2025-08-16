#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Don Trabajo GPT persona wrapper for gpt-oss:20b via Ollama.
- Auto-injects persona system prompt
- Lightweight “memory” (facts + rolling summary)
- Stream UX fixes (no early prompt label, soft lock during generation)
- News guard for offline model hallucinations
Requires: pip3 install requests
Run: python3 don_trabajo_oss.py
"""

import json
import os
import sys
import time
import requests
import warnings
from pathlib import Path

# Silence noisy LibreSSL warning on macOS system Python
try:
    from urllib3.exceptions import NotOpenSSLWarning
    warnings.filterwarnings("ignore", category=NotOpenSSLWarning)
except Exception:
    pass

# -------- Config ----------
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
MODEL       = os.environ.get("OSS_MODEL", "gpt-oss:20b")   # change if you tagged it differently
PERSONA_FN  = Path("persona_prompt.txt")
STATE_DIR   = Path(".don_trabajo_oss")
MEM_FN      = STATE_DIR / "memories.json"     # persistent user facts + rolling summary
HISTORY_FN  = STATE_DIR / "history.jsonl"     # raw chat log (for your own records)
MAX_CTX_MSGS = 18                              # keep context lean; adjust for longer chats
TEMPERATURE = float(os.environ.get("OSS_TEMPERATURE", 0.3))
NUM_CTX     = int(os.environ.get("OSS_NUM_CTX", 8192))     # adjust if you enabled bigger context
# --------------------------

STATE_DIR.mkdir(exist_ok=True)

def load_persona():
    if PERSONA_FN.exists():
        return PERSONA_FN.read_text(encoding="utf-8").strip()
    # Safe fallback if the file is missing
    return (
        "You are Don Trabajo GPT — a witty, sharp-edged but generous hacker-philosopher. "
        "Be practical, structured, and personable. Never break character."
    )

def load_memories():
    if MEM_FN.exists():
        try:
            return json.loads(MEM_FN.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "facts": [
            "User handle: Don Trabajo; company: Prox Offensive.",
            "Focus: offensive security, HTB/CPTS, branding, EN/ES bilingual."
        ],
        "rolling_summary": ""
    }

def save_memories(mem):
    MEM_FN.write_text(json.dumps(mem, ensure_ascii=False, indent=2), encoding="utf-8")

def append_history(role, content):
    with HISTORY_FN.open("a", encoding="utf-8") as f:
        rec = {"ts": int(time.time()), "role": role, "content": content}
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def ollama_chat(messages, stream=True):
    url = f"{OLLAMA_HOST}/api/chat"
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": stream,
        "options": {
            "temperature": TEMPERATURE,
            "num_ctx": NUM_CTX
        }
    }
    if stream:
        # Use a connect timeout and unlimited read timeout
        with requests.post(url, json=payload, stream=True, timeout=(10, None)) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line:
                    continue
                try:
                    chunk = json.loads(line.decode("utf-8"))
                except Exception:
                    continue
                yield chunk
    else:
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
        yield r.json()

def build_context(system_prompt, mem, history):
    msgs = [{"role": "system", "content": system_prompt}]
    if mem.get("facts"):
        msgs.append({"role": "system", "content": "Known user facts: " + "; ".join(mem["facts"])})
    if mem.get("rolling_summary"):
        msgs.append({"role": "system", "content": "Conversation summary so far: " + mem["rolling_summary"]})
    # Append recent history, trimmed
    recent = history[-(MAX_CTX_MSGS*2):] if len(history) > (MAX_CTX_MSGS*2) else history
    msgs.extend(recent)
    return msgs

def summarize(history, system_prompt):
    """Update rolling summary with a compact recap to keep context small."""
    if not history:
        return ""
    # Keep last ~20 messages to summarize
    to_summarize = history[-20:]
    sys_prompt = (
        system_prompt +
        "\nSummarize the conversation below into 6-10 bullet points focusing on user goals, preferences, and any decisions. "
        "Keep it under 150 words. No fluff."
    )
    msgs = [{"role": "system", "content": sys_prompt}]
    for m in to_summarize:
        msgs.append(m)
    chunks = list(ollama_chat(msgs, stream=False))
    try:
        content = chunks[0]["message"]["content"]
    except Exception:
        content = ""
    return content.strip()

def print_help():
    print("""
Slash commands:
  /mem add <text>      -> add a memory fact
  /mem list            -> list memory facts
  /mem clear           -> clear all memory facts
  /sum                 -> force-update rolling summary
  /temp <0.0-1.0>      -> set temperature
  /ctx <tokens>        -> set num_ctx (restart recommended)
  /help                -> show this help
  /quit                -> exit
""".strip())

def looks_like_news(q: str) -> bool:
    q = q.lower()
    keys = [
        "latest", "today", "breaking", "this week", "new cve",
        "cve-202", "news", "update", "released", "launched"
    ]
    return any(k in q for k in keys)

def main():
    # preload persona & state
    persona = load_persona()
    mem = load_memories()
    history = []

    print(f"🔥 Don Trabajo GPT wrapper on {MODEL} via Ollama @ {OLLAMA_HOST}")
    print("Type /help for commands. Persona loaded from persona_prompt.txt.\n")

    assistant_busy = False  # soft lock to prevent input during streaming

    while True:
        try:
            user = input("You ▷ ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not user:
            continue

        # commands
        if user.startswith("/"):
            parts = user.split(maxsplit=2)
            cmd = parts[0].lower()
            if cmd == "/help":
                print_help()
            elif cmd == "/quit":
                print("Bye!")
                break
            elif cmd == "/mem":
                if len(parts) < 2:
                    print("Usage: /mem add <text> | /mem list | /mem clear")
                else:
                    sub = parts[1].lower()
                    if sub == "add":
                        if len(parts) == 3 and parts[2].strip():
                            mem["facts"].append(parts[2].strip())
                            save_memories(mem)
                            print("✅ Memory added.")
                        else:
                            print("Provide text: /mem add <text>")
                    elif sub == "list":
                        if mem["facts"]:
                            for i, fact in enumerate(mem["facts"], 1):
                                print(f"{i}. {fact}")
                        else:
                            print("(no facts)")
                    elif sub == "clear":
                        mem["facts"] = []
                        save_memories(mem)
                        print("✅ Memory cleared.")
                    else:
                        print("Unknown /mem subcommand.")
            elif cmd == "/sum":
                mem["rolling_summary"] = summarize(history, persona)
                save_memories(mem)
                print("✅ Summary updated.")
            elif cmd == "/temp":
                if len(parts) == 2:
                    try:
                        val = float(parts[1])
                        if 0.0 <= val <= 1.0:
                            global TEMPERATURE
                            TEMPERATURE = val
                            print(f"✅ temperature = {TEMPERATURE}")
                        else:
                            print("Provide 0.0–1.0")
                    except ValueError:
                        print("Provide a float 0.0–1.0")
                else:
                    print("Usage: /temp 0.2")
            elif cmd == "/ctx":
                if len(parts) == 2:
                    try:
                        val = int(parts[1])
                        global NUM_CTX
                        NUM_CTX = val
                        print(f"✅ num_ctx = {NUM_CTX} (restart recommended)")
                    except ValueError:
                        print("Provide an integer, e.g., /ctx 16384")
                else:
                    print("Usage: /ctx 16384")
            else:
                print("Unknown command. /help for options.")
            continue

        if assistant_busy:
            print("…hold up, I’m still answering the previous message.")
            continue

        # Optional guard for "latest news" prompts on a local model
        if looks_like_news(user):
            print("⚠️ Heads-up: using a local offline model. I’ll answer, but verify any 'latest' specifics on the web.\n")

        assistant_busy = True

        # normal chat
        history.append({"role": "user", "content": user})
        messages = build_context(load_persona(), mem, history)

        # tiny status line while waiting for first token
        print("(thinking…)", flush=True)

        assistant_text = []
        printed_label = False
        try:
            for chunk in ollama_chat(messages, stream=True):
                if "message" in chunk and "content" in chunk["message"]:
                    piece = chunk["message"]["content"]
                    assistant_text.append(piece)
                    if not printed_label:
                        # print label only when the first content token arrives
                        print("DonTrabajo ▷ ", end="", flush=True)
                        printed_label = True
                    print(piece, end="", flush=True)
                if chunk.get("done"):
                    break
        except requests.exceptions.RequestException as e:
            print(f"\n[Connection error: {e}]")
            # remove the last user message to keep history clean on failure
            history.pop()
            assistant_busy = False
            continue

        print()  # newline after streaming
        final = "".join(assistant_text).strip()
        history.append({"role": "assistant", "content": final})
        append_history("user", user)
        append_history("assistant", final)

        assistant_busy = False

        # refresh rolling summary every 6 exchanges to keep context tight
        if len(history) % 12 == 0:
            mem["rolling_summary"] = summarize(history, persona)
            save_memories(mem)

if __name__ == "__main__":
    main()


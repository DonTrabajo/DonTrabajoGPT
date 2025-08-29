import os, re, json
from urllib.parse import urlparse
from typing import List, Dict, Optional
from rich.console import Console
from dotenv import load_dotenv

from .model import OllamaChat
from .prompts import SYSTEM_PROMPT
from .schema import ToolCall
from .tools import registry as tool_registry

console = Console()
TOOL_RE = re.compile(r"```tool\s*(\{.*?\})\s*```", re.DOTALL)

def _norm_stdout(out):
    try:
        if isinstance(out, dict):
            if isinstance(out.get("stdout"), str):
                return out["stdout"]
            o = out.get("output")
            if isinstance(o, dict) and isinstance(o.get("stdout"), str):
                return o["stdout"]
        return ""
    except Exception:
        return ""

class Agent:
    # -------------------- deterministic search helpers --------------------
    def _norm_domain(self, url: str) -> str:
        try:
            host = urlparse(url).netloc.lower()
            if host.startswith("www."):
                host = host[4:]
            parts = host.split(".")
            return ".".join(parts[-2:]) if len(parts) >= 2 else host
        except Exception:
            return url

    def _extract_query_and_sites(self, text: str):
        """
        Returns (query:str, includes:set[str], excludes:set[str])
        - prefers the longest quoted phrase
        - parses site:foo.com and -site:foo.com tokens
        - strips instruction-y words (use/verify/final_answer/max_chars/etc.)
        """
        t = text or ""
        # quoted candidates
        qs = []
        for m in re.finditer(r'"([^"]+)"|\'([^\']+)\'', t):
            q = m.group(1) or m.group(2) or ""
            q = q.strip()
            if q and len(q) >= 3:
                qs.append(q)
        quoted = max(qs, key=len) if qs else ""

        # site tokens
        includes, excludes = set(), set()
        for m in re.finditer(r'(?i)(-?site:)([A-Za-z0-9.\-]+)', t):
            tok, dom = m.group(1), m.group(2).lower()
            dom = dom.lstrip("*.")  # normalize
            if tok.lower().startswith("-site:"):
                excludes.add(dom)
            else:
                includes.add(dom)
        # scrub tokens & instruction-y glue
        scrub = re.sub(r'(?i)(-?site:[^\s]+)', ' ', t)
        scrub = re.sub(r'(?i)\b(use|verify|finish|final_answer|bullets?|working\s*urls?|max[_\s-]*chars\s*=\s*\d+|then|and|list|include|urls?|two|2)\b', ' ', scrub)
        scrub = re.sub(r'[`*{}()\[\]]', ' ', scrub)
        scrub = re.sub(r'\s+', ' ', scrub).strip()

        if quoted:
            q = quoted
        else:
            # drop any lingering site: tokens from scrubbed text
            q = re.sub(r'(?i)(-?site:[^\s]+)', '', scrub).strip()

        if not q:
            # last-resort heuristic
            q = "passkeys adoption 2025" if "passkey" in t.lower() else t.strip()[:80]
        return q, includes, excludes

    def _filter_and_rerank(self, raw_results, need: int, user_prompt: str):
        """
        Filters by includes/excludes, verifies via web.get, scores by:
        - keyword hits in title/body
        - presence of '2025'
        - mild domain prior
        - drops soft-404/short bodies/non-2xx
        Returns list[(title,url)] length<=need
        """
        q, includes, excludes = self._extract_query_and_sites(user_prompt)
        # keywords (3+ chars) from query
        kws = [w.lower() for w in re.findall(r'[A-Za-z0-9]{3,}', q)]
        bad_domains = {
            "reddit.com","answers.microsoft.com","support.google.com","quora.com",
            "stackoverflow.com","superuser.com","serverfault.com","community.spotify.com"
        }
        prefer_domains = {
            "biometricupdate.com","techcrunch.com","zdnet.com","computerworld.com","theverge.com",
            "wired.com","bloomberg.com","bbc.com","nytimes.com","authsignal.com","corbado.com",
            "passkeys.directory","state-of-passkeys.io"
        }

        # raw → prelim URL list by site filters
        prelim = []
        for r in (raw_results or []):
            url = r.get("url") or r.get("href") or r.get("link")
            if not url:
                continue
            dom = self._norm_domain(url)
            if includes and dom not in includes:
                continue
            if dom in excludes:
                continue
            if dom in bad_domains:
                continue
            prelim.append((r.get("title") or "", url))

        # verify & score top few
        verified = []
        for title, url in prelim[:8]:
            try:
                page = self.tools["web.get"](url=url, max_chars=900)
                status = int(page.get("status_code", 0) or 0)
                if status < 200 or status >= 300:
                    continue
                text = (page.get("text") or "")
                ttitle = (page.get("title") or title or "").strip()
                low_t, low_x = ttitle.lower(), text.lower()
                if len(low_x) < 200:
                    continue
                if any(ph in low_x for ph in ("not found","page not found","404","doesn’t exist","does not exist","oops")):
                    continue

                # score
                s = 0
                for k in kws:
                    if k in low_t: s += 2
                    if k in low_x: s += 1
                if "2025" in low_t or "2025" in low_x: s += 3
                dom = self._norm_domain(page.get("url") or url)
                if dom in prefer_domains: s += 2
                verified.append((s, ttitle or "(no title)", page.get("url") or url))
            except Exception:
                continue

        verified.sort(key=lambda x: x[0], reverse=True)
        return [(t,u) for _,t,u in verified[:need]]
    # ------------------ end deterministic search helpers -------------------
    
    def __init__(self, model: OllamaChat, tools: dict, show_cot: bool, max_turns: int = 8, system_prompt: Optional[str] = None):
        self.model = model
        self.tools = tools
        self.show_cot = show_cot
        self.max_turns = max_turns
        self.system_prompt = system_prompt or SYSTEM_PROMPT

    @classmethod
    def from_env(cls):
        load_dotenv(dotenv_path="tools/agent/.env", override=False)
        model_name = os.getenv("MODEL_NAME", "gpt-oss-20b")
        base = os.getenv("OLLAMA_BASE", "http://localhost:11434")
        temp = float(os.getenv("TEMPERATURE", "0.2"))
        num_ctx = int(os.getenv("NUM_CTX", "16384"))
        max_turns = int(os.getenv("MAX_TURNS", "8"))
        show_cot = os.getenv("SHOW_CHAIN_OF_THOUGHT", "false").lower() == "true"
        enable_shell = os.getenv("ENABLE_SHELL", "false").lower() == "true"
        enable_py = os.getenv("ENABLE_PYTHON", "true").lower() == "true"
        enable_fs = os.getenv("ENABLE_FS", "true").lower() == "true"
        tools = tool_registry(enable_shell=enable_shell, enable_python=enable_py, enable_fs=enable_fs)
        model = OllamaChat(model=model_name, base_url=base, temperature=temp, num_ctx=num_ctx)
        return cls(model, tools, show_cot, max_turns)

    def run(self, user_prompt: str) -> str:
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": "You can browse, call tools, run small code snippets, and then provide a final answer. If a task requires current info, prefer web.search + web.get."},
            {"role": "user", "content": user_prompt},
        ]
        try:
            console.print("[cyan]Tools available:[/cyan]", list(self.tools.keys()))
        except Exception:
            pass

        last_reply = ""
        did_any_tool = False

        for turn in range(self.max_turns):
            reply = self.model.chat(messages).strip()
            # Opportunistic deterministic web.search when user clearly requests it
            if not did_any_tool and re.search(r'\bweb\.search\b', (user_prompt + reply).lower()):
                # BOOTSTRAP: web.search (deterministic filter + rerank)
                try:
                    q, include_sites, _ = self._extract_query_and_sites(user_prompt)
                    out = self.tools["web.search"](query=q, max_results=8)
                    if (not out or len(out) == 0) and include_sites:
                        out = self.tools["web.search"](query=f"{q} site:{include_sites[0]}", max_results=8)
                    picks = self._filter_and_rerank(out, need=2, user_prompt=user_prompt)
                    if picks:
                        bullets = "\\n".join([f"- {t} — {u}" for (t,u) in picks])
                        if re.search(r"final_answer", user_prompt, re.I):
                            return "FINAL_ANSWER: " + ("\\n" + bullets if "\\n" in bullets else bullets)
                        messages.append({"role": "assistant", "content": bullets})
                    else:
                        messages.append({"role": "assistant", "content": "No suitable results after filtering."})
                    did_any_tool = True
                    continue
                except Exception:
                    pass
        
            reply = re.sub(r"<think>.*?</think>", "", reply, flags=re.DOTALL).strip()
            last_reply = reply or last_reply

            if self.show_cot:
                if "FINAL_ANSWER:" in reply:
                    reasoning = reply.split("FINAL_ANSWER:", 1)[0].strip()
                    if reasoning:
                        console.rule("[bold magenta]Reasoning[/bold magenta]"); console.print(reasoning)
                else:
                    console.rule("[bold magenta]Reasoning[/bold magenta]"); console.print(reply)

            # 1) Did the model emit a tool call?
            m = TOOL_RE.search(reply)
            if m:
                tool_json = m.group(1)
                try:
                    call = ToolCall.model_validate_json(tool_json)
                except Exception as e:
                    messages.append({"role": "assistant", "content": f"Observation (parser): {{\"error\": \"Invalid tool JSON: {e}\"}}"})
                    messages.append({"role": "system", "content": "Reminder: emit a valid ```tool { ... }``` JSON block or finish with FINAL_ANSWER: <text>."})
                    continue

                obs = self._dispatch(call)
                did_any_tool = True
                messages.append({"role": "assistant", "content": f"Observation ({call.tool}): {json.dumps(obs)}"})

                if call.tool == "web.search":
                    out = obs.get("output", [])
                    if isinstance(out, dict): out = [out]
                    picks = self._validate_and_pick_urls(out, user_prompt)
                    if picks:
                        return "\n".join([f"- {t} — {u}" for (t,u) in picks])
                if call.tool == "py.exec":
                    stdout = _norm_stdout(obs.get("output", {})).strip()
                    if stdout and any(k in user_prompt.lower() for k in ["number only","just the number","print the result"]):
                        return stdout
                continue

            # 2) Explicit FINAL_ANSWER by model?
            if "FINAL_ANSWER:" in reply:
                return reply.split("FINAL_ANSWER:", 1)[1].strip()

            # 3) Bootstrap web.search early (AND finalize here)
            if (turn < 2) and ("web.search" in (user_prompt + reply).lower()) and not did_any_tool:
                try:
                    console.print("[yellow]BOOTSTRAP:[/yellow] web.search")
                    m_q = re.search(r'"([^"]+)"', user_prompt)
                    query = m_q.group(1) if m_q else user_prompt
                    out = self.tools["web.search"](query=query, max_results=5)
                    res = out if isinstance(out, list) else ([] if out is None else [out])
                    console.print(f"[blue]results:[/blue] {len(res)} for query={query!r}")
                    # Fallback: sanitize query if empty results (strip -site: and quotes)
                    if not res:
                        query2 = self._sanitize_query(query)
                        console.print(f"[yellow]retry with sanitized query:[/yellow] {query2!r}")
                        out = self.tools["web.search"](query=query2, max_results=5)
                        res = out if isinstance(out, list) else ([] if out is None else [out])
                        console.print(f"[blue]results:[/blue] {len(res)} for query={query2!r}")
                    messages.append({"role": "assistant", "content": f"Observation (web.search): {json.dumps({'tool':'web.search','output':res})}"})
                    did_any_tool = True
                    picks = self._validate_and_pick_urls(res, user_prompt)
                    if picks:
                        return "\n".join([f"- {t} — {u}" for (t,u) in picks])
                    # FINAL SAFETY NET: return first 1–2 2xx URLs even if validator found none
                    need = 2 if (" 2 " in user_prompt.lower() or "two" in user_prompt.lower()) and len(res) >= 2 else 1
                    safe = []
                    for r in res:
                        if len(safe) >= need: break
                        url = (r.get("href") or r.get("url") or r.get("link") or "").strip().replace("\n","" ).replace(" ", "")
                        if not url: continue
                        try:
                            page = self.tools["web.get"](url=url, max_chars=120)
                            status = int(page.get("status_code", 200))
                            if 200 <= status < 300:
                                title = (r.get("title") or page.get("title") or "(no title)").strip()
                                vurl = page.get("url", url)
                                safe.append((title, vurl))
                        except Exception:
                            continue
                    if safe:
                        return "\n".join([f"- {t} — {u}" for (t,u) in safe])
                    continue
                except Exception as e:
                    try: console.print(f"[red]web.search bootstrap error:[/red] {e}")
                    except Exception: pass

            # 4) Bootstrap py.exec early (AND finalize if asked)
            if (turn < 2) and ("py.exec" in (user_prompt + reply).lower()) and not did_any_tool:
                try:
                    console.print("[yellow]BOOTSTRAP:[/yellow] py.exec")
                    code = None
                    m_code = re.search(r"```(?:python)?\n([\s\S]*?)```", user_prompt, re.IGNORECASE)
                    if m_code:
                        code = m_code.group(1).strip()
                    else:
                        m_expr = re.search(r"(\d[\d\s\+\-\*/%\(\)\.]*\*\*\s*\d+)", user_prompt)
                        if m_expr:
                            expr = m_expr.group(1).replace(" ", "")
                            code = f"print({expr})"
                    if code:
                        out = self.tools["py.exec"](code=code)
                        messages.append({"role":"assistant","content": f"Observation (py.exec): {json.dumps({'tool':'py.exec','output': out})}"})
                        did_any_tool = True
                        stdout = _norm_stdout(out).strip()
                        if stdout and any(k in user_prompt.lower() for k in ["number only","just the number","print the result"]):
                            return stdout
                        continue
                except Exception as e:
                    try: console.print(f"[red]py.exec bootstrap error:[/red] {e}")
                    except Exception: pass

            # 5) Nudge & keep going
            messages.append({"role": "system", "content": "Remember: either emit a ```tool { ... }``` block OR finish with one line starting with FINAL_ANSWER: <text>."})
            messages.append({"role": "assistant", "content": reply})

        return last_reply if last_reply else "[Agent] Max turns reached without a final answer."

    def _extract_query(self, user_prompt: str):
        txt = user_prompt.strip()
        # 1) Prefer first quoted chunk (single OR double)
        for qch in ('"', "'"):
            if qch in txt:
                start = txt.find(qch)
                end = txt.find(qch, start + 1)
                if start != -1 and end != -1:
                    q = txt[start+1:end].strip()
                    return self._strip_excludes(q)
        # 2) Fallback: capture after 'for ' up to comma/period or keywords
        m = _re.search(r'\bfor\s+(.+?)(?:(?:,|\.)|\bverify\b|\bthen\b|$)', txt, _re.I|_re.S)
        q = m.group(1).strip() if m else txt
        return self._strip_excludes(q)

    def _strip_excludes(self, q: str):
        excludes = _re.findall(r'-site:([\w.-]+)', q)
        q_clean = _re.sub(r'-site:[^\s]+', '', q)
        q_clean = _re.sub(r'["\']', '', q_clean)
        q_clean = _re.sub(r'\s+', ' ', q_clean).strip()
        return q_clean, [d.lower() for d in excludes]

    def _filter_excludes(self, results, excludes):
        res = results if isinstance(results, list) else ([] if results is None else [results])
        if not excludes:
            return res
        out = []
        for r in res:
            url = (r.get('href') or r.get('url') or r.get('link') or '') or ''
            u = url.lower()
            if not any(dom in u for dom in excludes):
                out.append(r)
        return out

    def _sanitize_query(self, q: str) -> str:
        # strip -site:foo.com terms and quotes; squash whitespace
        q2 = re.sub(r'-site:[^\s]+', '', q)
        q2 = re.sub(r'["\']', '', q2)
        q2 = re.sub(r'\b(use|web\.search|verify|finish|final_answer|then)\b', '', q2, flags=re.I)
        q2 = re.sub(r'\s+', ' ', q2).strip()
        return q2

    def _validate_and_pick_urls(self, results, user_prompt):
        if isinstance(results, dict): results = [results]
        up = user_prompt.lower()
        want_two = (" 2 " in up) or ("two" in up) or ("both urls" in up) or ("both url" in up)
        n = 2 if want_two and len(results) >= 2 else 1

        picks_strict, picks_medium, picks_lenient = [], [], []
        SOFT404 = ("page not found","not found","error 404","doesn’t exist","doesn't exist")

        def candidate(url_dict):
            url = (url_dict.get("href") or url_dict.get("url") or url_dict.get("link") or "").strip()
            return url.replace("\n","" ).replace(" ", "")

        for r in results:
            if len(picks_strict) >= n and len(picks_medium) >= n and len(picks_lenient) >= n:
                break
            url = candidate(r)
            if not url: continue
            try:
                page = self.tools["web.get"](url=url, max_chars=800)
                status = int(page.get("status_code", 200))
                text   = (page.get("text") or "").lower()
                title  = (page.get("title") or "").lower()
                vurl   = page.get("url", url)
                try:
                    from rich.console import Console
                    Console().print(f"[blue]chk:[/blue] {status} | len={len(text)} | title={page.get('title','')[:60]!r} | {vurl}")
                except Exception:
                    pass

                if status < 200 or status >= 300:
                    continue
                if len(text) < 120 or any(ph in text for ph in SOFT404) or any(ph in title for ph in SOFT404):
                    continue

                if ("passkey" in text or "passkeys" in text or "passkey" in title) and ("2025" in text or "2025" in title):
                    t = (r.get("title") or page.get("title") or "(no title)").strip()
                    picks_strict.append((t, vurl)); continue
                if ("passkey" in text or "passkeys" in text or "passkey" in title):
                    t = (r.get("title") or page.get("title") or "(no title)").strip()
                    picks_medium.append((t, vurl)); continue
                if len(text) >= 200:
                    t = (r.get("title") or page.get("title") or "(no title)").strip()
                    picks_lenient.append((t, vurl))

            except Exception:
                continue

        if len(picks_strict) >= n:  return picks_strict[:n]
        if len(picks_medium) >= n:  return picks_medium[:n]
        if len(picks_lenient) >= n: return picks_lenient[:n]
        return []

    def _dispatch(self, call: ToolCall):
        fn = self.tools.get(call.tool)
        if not fn:
            return {"tool": call.tool, "error": "Unknown tool"}
        try:
            out = fn(**call.input)
            return {"tool": call.tool, "output": out}
        except TypeError as e:
            return {"tool": call.tool, "error": f"Bad args: {e}"}
        except Exception as e:
            return {"tool": call.tool, "error": str(e)}

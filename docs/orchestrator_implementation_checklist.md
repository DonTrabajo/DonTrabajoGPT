# Orchestrator Implementation Checklist

**Reference:** See `docs/orchestrator_design.md` for full API specs and design rationale.

**Goal:** Implement the orchestrator module and wire it into the TUI to centralize workflow logic.

---

## Phase 1: Core Orchestrator Implementation

### Step 1: Create Module Skeleton
- [ ] Create `orchestrator.py` in repo root
- [ ] Add module docstring explaining its role (see design doc § 1)
- [ ] Add imports:
  ```python
  import os
  import json
  import requests
  from datetime import datetime
  from pathlib import Path
  from dotenv import load_dotenv
  from typing import Literal

  # Pipeline modules
  from linpeas_preprocessor import preprocess_linpeas_output
  from linpeas_parser import parse_linpeas_output
  from cve_matcher import _match_cves
  from gpt_analysis import format_prompt, _get_client
  from tools.oss_persona.oss_client import quick_answer
  ```

### Step 2: Implement Helper Functions
- [ ] `_check_ollama_available() -> bool`
  - Ping `$OLLAMA_HOST/api/tags` with 2 second timeout
  - Return True if status code 200, False otherwise

- [ ] `_check_openai_available() -> bool`
  - Load .env and check if `OPENAI_API_KEY` is set
  - Return True if key exists and is non-empty

- [ ] `_generate_timestamp_filename(prefix: str = "linpeas_parsed") -> str`
  - Return `f"{prefix}_{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"`

### Step 3: Implement LLM Routing
- [ ] `detect_llm_backend(mode: str = "auto") -> Literal["local", "cloud", "none"]`
  - Implement decision tree from design doc § 3.2
  - If mode=="local": return "local" if ollama available else "none"
  - If mode=="cloud": return "cloud" if openai available else "none"
  - If mode=="auto": prefer local → cloud → none
  - If mode=="none": return "none"
  - Raise ValueError for unknown modes

- [ ] `get_llm_status() -> dict`
  - Return availability status for both backends
  - Schema from design doc Appendix A

### Step 4: Implement Core Analysis Functions

- [ ] `validate_linpeas_json(json_path: str) -> dict`
  - Load JSON file
  - Check `metadata.schema == "don-trabajo-linpeas-v1"`
  - Check required fields: users, suid_binaries, kernel, binaries
  - Return validation dict (see design doc § 2.5)

- [ ] `preprocess_only(raw_file_path: str, output_path: str | None = None) -> dict`
  - Generate output path if None (use `_generate_timestamp_filename()`)
  - Call `preprocess_linpeas_output(raw_file_path, output_path)`
  - Load the generated JSON
  - Return dict: `{"status": "success"|"error", "json_path": str, "parsed_data": dict, "error": str|None}`
  - Wrap in try/except for FileNotFoundError and general Exception

- [ ] `run_cve_pipeline(json_path: str) -> dict`
  - Load JSON from path
  - Validate schema (call `validate_linpeas_json()`)
  - Extract binaries: `data.get("binaries", [])`
  - Call `_match_cves(binaries)` from cve_matcher
  - Return dict: `{"status": "success"|"error", "cve_findings": list, "error": str|None}`

- [ ] `summarize_findings(json_path: str | None = None, parsed_data: dict | None = None, mode: str = "auto") -> dict`
  - Validate that exactly one of json_path or parsed_data is provided
  - If json_path: load and parse JSON
  - Detect backend: `backend = detect_llm_backend(mode)`
  - If backend == "none": return early with status="error"
  - If backend == "local":
    - Format findings into prompt (users, suids, kernel, IPs, binaries)
    - Call `oss_client.quick_answer(prompt, system=<persona>)`
  - If backend == "cloud":
    - Call `format_prompt(parsed_data)` from gpt_analysis
    - Get client via `_get_client()`
    - If client is None: return error status
    - Make API call, extract response
  - Return dict: `{"status": "success"|"error", "summary": str|None, "backend_used": str, "error": str|None}`

- [ ] `analyze_linpeas(raw_file_path: str, mode: str = "auto", save_json: bool = False) -> dict`
  - Generate temp JSON path: `json_path = _generate_timestamp_filename()`
  - Initialize result dict with all fields
  - Wrap entire workflow in try/finally
  - **Try block:**
    1. Call `preprocess_only(raw_file_path, json_path)`
    2. Load JSON: `parsed_data = json.load(open(json_path))`
    3. Call `run_cve_pipeline(json_path)` → extract cve_findings
    4. If mode != "none": call `summarize_findings(parsed_data=parsed_data, mode=mode)`
    5. Populate result dict with all data
  - **Finally block:**
    - If save_json == False and json_path exists: `os.remove(json_path)`
    - Set result["json_path"] = json_path if save_json else None
  - Return result dict (see design doc Appendix A for schema)

### Step 5: Implement Agent Functions

- [ ] `launch_agent_session(persona: str = "don_trabajo", mode: str = "local") -> None`
  - Import `from tools.agent.runner import repl`
  - Load dotenv from `tools/agent/.env`
  - Call `repl()` (blocking)
  - Return when user exits

- [ ] `agent_one_shot(query: str, persona: str = "don_trabajo", mode: str = "local") -> dict`
  - Import `from tools.agent.agent import Agent`
  - Create agent: `agent = Agent.from_env()`
  - Call `response = agent.run(query)`
  - Return dict: `{"status": "success", "response": response, "error": None}`
  - Wrap in try/except, return error dict on failure

---

## Phase 2: Refactor Existing Modules (Optional Cleanup)

- [ ] Update `combo_linpeas_analyzer.py`:
  - Add deprecation notice in docstring
  - Optionally rewrite as thin wrapper calling `orchestrator.analyze_linpeas()`

- [ ] Verify `cve_matcher._match_cves()` is importable (already is)
- [ ] Verify `gpt_analysis.format_prompt()` and `_get_client()` are importable (already are)

---

## Phase 3: Wire Orchestrator into TUI

### Update `don_trabajo_gpt.py`

- [ ] Add import at top: `import orchestrator`

- [ ] **Option 0** (Preprocess linPEAS):
  ```python
  elif choice == "0":
      file_path = _prompt_for_file("📄 Preprocess raw linPEAS .txt to JSON: ")
      if not file_path:
          continue

      result = orchestrator.preprocess_only(file_path)

      if result["status"] == "success":
          console.print(f"[green]✓ JSON saved to: {result['json_path']}[/green]")
      else:
          console.print(f"[red]✗ Preprocessing failed: {result['error']}[/red]")

      input("\n[Press Enter to return to menu]")
      swoosh_transition()
  ```

- [ ] **Option 2** (CVE Matcher):
  ```python
  elif choice == "2":
      file_path = _prompt_for_file("📄 Enter path to linPEAS JSON output file: ")
      if not file_path:
          continue
      console.print("\a", end="")
      animated_transition()

      result = orchestrator.run_cve_pipeline(file_path)

      if result["status"] == "success":
          if result["cve_findings"]:
              console.print("\n✅  [bold green]CVE Findings:[/bold green]")
              console.print("-" * 40)
              for hit in result["cve_findings"]:
                  console.print(f"• [bold]{hit['name']}[/bold] {hit['version']}")
                  console.print(f"   CVE: {hit['cve']}")
                  console.print(f"   Desc: {hit['description']}\n")
          else:
              console.print("ℹ No vulnerable binaries found.", style="bold green")
      else:
          console.print(f"[red]✗ CVE matching failed: {result['error']}[/red]")

      console.print("\a", style="green", end="")
      input("\n[Press Enter to return to menu]")
      swoosh_transition()
  ```

- [ ] **Option 6** (Offline LLM):
  ```python
  elif choice == "6":
      try:
          orchestrator.launch_agent_session(persona="don_trabajo", mode="local")
      except Exception as exc:
          console.print(f"[red]✗ Offline LLM failed: {exc}[/red]")
      input("\n[Press Enter to return to menu]")
      swoosh_transition()
  ```

- [ ] **Option 7** (Full linPEAS Analyzer):
  ```python
  elif choice == "7":
      file_path = _prompt_for_file("📄 Enter path to raw linPEAS .txt for full-stack analysis: ")
      if not file_path:
          continue
      animated_transition()

      console.print(Panel("[bold magenta]💻 Starting Full Stack Analysis[/bold magenta]", border_style="bright_magenta"))
      result = orchestrator.analyze_linpeas(file_path, mode="auto", save_json=False)

      if result["status"] in ["success", "partial"]:
          # Display parsed summary
          console.print(Panel("[bold cyan]📜 Parsed Summary[/bold cyan]", border_style="bright_cyan"))
          data = result["parsed_data"]
          console.print(f"[bold yellow]Users:[/bold yellow] {', '.join(data.get('users', []))}")
          console.print(f"[bold yellow]SUID Binaries:[/bold yellow] {len(data.get('suid_binaries', []))} found")
          console.print(f"[bold yellow]Kernel:[/bold yellow] {data.get('kernel', {}).get('version', 'unknown')}")

          # Display CVE findings
          if result["cve_findings"]:
              console.print(Panel("[bold yellow]🛡 CVE Findings[/bold yellow]", border_style="yellow"))
              for cve in result["cve_findings"]:
                  console.print(f"• {cve['cve']}: {cve['description']}")

          # Display LLM summary if available
          if result["llm_summary"]:
              console.print(Panel("[bold blue]🧠 AI Summary[/bold blue]", border_style="blue"))
              console.print(result["llm_summary"])

          console.print("\n[green]✓ Analysis complete[/green]")
      else:
          console.print(f"[red]✗ Analysis failed: {', '.join(result['errors'])}[/red]")

      input("\n[Press Enter to return to menu]")
      swoosh_transition()
  ```

- [ ] **Remove old imports** (no longer needed for workflows):
  ```python
  # DELETE these lines:
  from combo_linpeas_analyzer import analyze_linpeas_full_stack
  from linpeas_preprocessor import preprocess_linpeas_output
  from cve_matcher import run_cve_matcher
  ```

- [ ] **Keep these imports** (still used):
  ```python
  from linpeas_parser import parse_linpeas_output  # Option 1 still uses this
  from validate_tool_paths import validate_tool_paths  # Option 3
  from animated_transition import animated_transition
  from swoosh_transition import swoosh_transition
  ```

---

## Phase 4: Testing

### Manual Test Cases

- [ ] **Test preprocess_only:**
  ```bash
  python3 -c "import orchestrator; print(orchestrator.preprocess_only('sample_linpeas.txt'))"
  ```

- [ ] **Test LLM status:**
  ```bash
  python3 -c "import orchestrator; print(orchestrator.get_llm_status())"
  ```

- [ ] **Test full analysis with mode="none":**
  - Run menu option 7 with a sample linPEAS file
  - Should complete without LLM summary

- [ ] **Test full analysis with mode="local"** (requires Ollama running):
  - Temporarily modify option 7 to use `mode="local"`
  - Verify Ollama summary appears

- [ ] **Test full analysis with mode="cloud"** (requires API key):
  - Temporarily modify option 7 to use `mode="cloud"`
  - Verify OpenAI summary appears

- [ ] **Test auto-routing:**
  - Run with only Ollama available → should use local
  - Run with only OpenAI available → should use cloud
  - Run with neither available → should return partial results

- [ ] **Test temp file cleanup:**
  - Run option 7 with `save_json=False`
  - Verify no temp JSON files left in directory

- [ ] **Test agent session:**
  - Run menu option 6
  - Type a query
  - Verify response from local agent
  - Type 'exit' to quit

---

## Phase 5: Documentation

- [ ] Add docstrings to all orchestrator functions (Google-style)
- [ ] Update `README.md` with architecture overview section
- [ ] Add example usage to README:
  ```python
  import orchestrator

  # Full analysis with local LLM
  result = orchestrator.analyze_linpeas("linpeas.txt", mode="local")
  print(result["llm_summary"])

  # Just CVE matching
  cve_result = orchestrator.run_cve_pipeline("linpeas.json")
  for finding in cve_result["cve_findings"]:
      print(finding["cve"])
  ```

---

## Success Criteria

✅ **Orchestrator module exists** and all functions are implemented
✅ **Menu options 0, 2, 6, 7** use orchestrator instead of direct module calls
✅ **LLM auto-routing works**: local → cloud → none fallback
✅ **All manual tests pass** without errors
✅ **No Rich console calls** inside orchestrator.py (returns data only)
✅ **Temp files cleaned up** when save_json=False
✅ **Error handling** returns structured dicts, not exceptions

---

## Notes

- **Don't refactor Option 1** (Parse linPEAS) unless requested—it's purely presentational
- **Don't touch Option 3** (Tool Validation)—orthogonal to analysis pipeline
- **Leave Options 4 & 5** as placeholders (not implemented yet)
- **Preserve all existing error messages** and styling patterns from current code
- **Test incrementally**: Implement Step 1-3 → test helpers → implement Step 4 → test core functions → implement Step 5 → test TUI integration

---

**Estimated Time:** 4-6 hours for implementation, 1-2 hours for testing

**Reference:** Full API specs and return schemas in `docs/orchestrator_design.md`

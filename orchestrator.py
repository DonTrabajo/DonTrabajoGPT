"""
Workflow orchestrator for DonTrabajoGPT.

Bridges the TUI/CLI with analysis modules (linPEAS preprocessing, CVE matching,
and LLM summarization), handles backend routing, and exposes agent entrypoints.
All functions return structured data; presentation is handled by callers.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional

import requests
from dotenv import load_dotenv

from linpeas_preprocessor import preprocess_linpeas_output
from linpeas_parser import parse_linpeas_output  # noqa: F401 - exposed for callers if needed
from cve_matcher import _match_cves
from gpt_analysis import format_prompt, _get_client
from tools.oss_persona.oss_client import quick_answer


load_dotenv()


def _generate_timestamp_filename(prefix: str = "linpeas_parsed") -> str:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{prefix}_{ts}.json"


def _check_ollama_available() -> bool:
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    try:
        r = requests.get(f"{host}/api/tags", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


def _check_openai_available() -> bool:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    return bool(api_key and api_key.strip())


def detect_llm_backend(mode: str = "auto") -> Literal["local", "cloud", "none"]:
    """
    Determine which LLM backend to use.

    Args:
        mode: Requested backend ("local", "cloud", "auto", or "none").

    Returns:
        Resolved backend identifier.
    """
    mode = (mode or "auto").lower()
    if mode == "local":
        return "local" if _check_ollama_available() else "none"
    if mode == "cloud":
        return "cloud" if _check_openai_available() else "none"
    if mode == "none":
        return "none"
    if mode == "auto":
        if _check_ollama_available():
            return "local"
        if _check_openai_available():
            return "cloud"
        return "none"
    raise ValueError(f"Unknown mode: {mode}")


def get_llm_status() -> dict:
    """
    Report availability of local and cloud LLM backends.

    Returns:
        Dict with availability details for local and cloud backends.
    """
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    local_available = _check_ollama_available()
    cloud_key = os.getenv("OPENAI_API_KEY")
    cloud_available = bool(cloud_key and cloud_key.strip())

    return {
        "local": {
            "available": local_available,
            "endpoint": host,
            "model": os.getenv("LLM_MODEL", ""),
        },
        "cloud": {
            "available": cloud_available,
            "api_key_set": cloud_available,
            "model": os.getenv("LLM_MODEL", "gpt-3.5-turbo"),
        },
    }


def validate_linpeas_json(json_path: str) -> dict:
    """
    Validate that the JSON matches expected linPEAS schema.

    Args:
        json_path: Path to linPEAS JSON file.

    Returns:
        Dict with validation status, schema, version, and any missing fields/warnings.
    """
    result = {"valid": False, "schema": None, "version": None, "missing_fields": [], "warnings": []}
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        meta = data.get("metadata", {})
        result["schema"] = meta.get("schema")
        result["version"] = meta.get("version")
        if result["schema"] != "don-trabajo-linpeas-v1":
            result["warnings"].append("Unexpected schema version")
        required = ["users", "suid_binaries", "kernel", "binaries"]
        missing = [k for k in required if k not in data]
        result["missing_fields"] = missing
        result["valid"] = not missing
    except FileNotFoundError:
        result["warnings"].append(f"File not found: {json_path}")
    except Exception as exc:
        result["warnings"].append(f"Validation error: {exc}")
    return result


def preprocess_only(raw_file_path: str, output_path: Optional[str] = None) -> dict:
    """
    Run preprocessing on raw linPEAS text and return JSON path and parsed data.

    Args:
        raw_file_path: Path to linPEAS .txt output.
        output_path: Optional custom output path; auto-generated if omitted.

    Returns:
        Dict with status, json_path, parsed_data, and error (if any).
    """
    out_path = output_path or _generate_timestamp_filename()
    try:
        preprocess_linpeas_output(raw_file_path, out_path)
        with open(out_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {"status": "success", "json_path": out_path, "parsed_data": data, "error": None}
    except FileNotFoundError as exc:
        return {"status": "error", "json_path": None, "parsed_data": None, "error": f"File not found: {exc}"}
    except Exception as exc:
        return {"status": "error", "json_path": None, "parsed_data": None, "error": str(exc)}


def run_cve_pipeline(json_path: str) -> dict:
    """
    Run CVE matching against a linPEAS JSON file.

    Args:
        json_path: Path to linPEAS JSON.

    Returns:
        Dict with status, CVE findings list, and error (if any).
    """
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        val = validate_linpeas_json(json_path)
        if not val.get("valid"):
            return {"status": "error", "cve_findings": [], "error": f"Invalid schema: {val.get('missing_fields')}"}
        findings = _match_cves(data.get("binaries", []))
        return {"status": "success", "cve_findings": findings, "error": None}
    except FileNotFoundError as exc:
        return {"status": "error", "cve_findings": [], "error": f"File not found: {exc}"}
    except Exception as exc:
        return {"status": "error", "cve_findings": [], "error": str(exc)}


def summarize_findings(
    json_path: Optional[str] = None, parsed_data: Optional[dict] = None, mode: str = "auto"
) -> dict:
    """
    Generate an LLM summary for linPEAS findings using local or cloud backend.

    Args:
        json_path: Path to linPEAS JSON (optional if parsed_data provided).
        parsed_data: Parsed linPEAS data (optional).
        mode: LLM backend selection ("local", "cloud", "auto", "none").

    Returns:
        Dict with status, summary text, backend_used, and error.
    """
    provided = sum(1 for v in [json_path, parsed_data] if v)
    if provided != 1:
        return {"status": "error", "summary": None, "backend_used": None, "error": "Provide exactly one of json_path or parsed_data"}
    if mode == "none":
        return {"status": "error", "summary": None, "backend_used": None, "error": "LLM summarization disabled (mode=none)"}
    if json_path and not parsed_data:
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                parsed_data = json.load(f)
        except Exception as exc:
            return {"status": "error", "summary": None, "backend_used": None, "error": str(exc)}
    if not parsed_data:
        return {"status": "error", "summary": None, "backend_used": None, "error": "No data provided for summarization"}

    backend = detect_llm_backend(mode)
    prompt = format_prompt(parsed_data)

    if backend == "local":
        try:
            summary = quick_answer(prompt, system=None)
            return {"status": "success", "summary": summary, "backend_used": "local", "error": None}
        except Exception as exc:
            return {"status": "error", "summary": None, "backend_used": "local", "error": str(exc)}

    if backend == "cloud":
        client = _get_client()
        if not client:
            return {"status": "error", "summary": None, "backend_used": "cloud", "error": "OpenAI client unavailable"}
        try:
            resp = client.chat.completions.create(
                model=os.getenv("LLM_MODEL", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": "You are a red team operations assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=700,
            )
            content = resp.choices[0].message.content
            return {"status": "success", "summary": content, "backend_used": "cloud", "error": None}
        except Exception as exc:
            return {"status": "error", "summary": None, "backend_used": "cloud", "error": str(exc)}

    return {"status": "error", "summary": None, "backend_used": None, "error": "LLM backend unavailable"}


def analyze_linpeas(raw_file_path: str, mode: str = "auto", save_json: bool = False) -> dict:
    """
    Full linPEAS workflow: preprocess -> CVE match -> optional LLM summary.

    Args:
        raw_file_path: Path to raw linPEAS text.
        mode: LLM mode ("auto", "local", "cloud", "none").
        save_json: Preserve intermediate JSON if True.

    Returns:
        Aggregated result dict with parsed data, CVE findings, LLM summary, and errors.
    """
    errors = []
    json_path = _generate_timestamp_filename()
    parsed_data = {}
    cve_findings = []
    llm_summary = None

    try:
        pre = preprocess_only(raw_file_path, json_path)
        if pre["status"] != "success":
            return {
                "status": "error",
                "json_path": None,
                "parsed_data": {},
                "cve_findings": [],
                "llm_summary": None,
                "errors": [pre.get("error")],
            }
        parsed_data = pre.get("parsed_data") or {}

        cve_result = run_cve_pipeline(json_path)
        if cve_result["status"] == "success":
            cve_findings = cve_result.get("cve_findings", [])
        else:
            errors.append(cve_result.get("error"))

        if mode != "none":
            sum_result = summarize_findings(json_path=json_path, parsed_data=parsed_data, mode=mode)
            if sum_result["status"] == "success":
                llm_summary = sum_result.get("summary")
            else:
                errors.append(sum_result.get("error"))
        status = "success" if not errors else "partial"
        return {
            "status": status,
            "json_path": json_path if save_json else None,
            "parsed_data": parsed_data,
            "cve_findings": cve_findings,
            "llm_summary": llm_summary,
            "errors": [e for e in errors if e],
        }
    except FileNotFoundError as exc:
        return {
            "status": "error",
            "json_path": None,
            "parsed_data": {},
            "cve_findings": [],
            "llm_summary": None,
            "errors": [f"File not found: {exc}"],
        }
    except Exception as exc:
        return {
            "status": "error",
            "json_path": None,
            "parsed_data": {},
            "cve_findings": [],
            "llm_summary": None,
            "errors": [f"Unexpected error: {exc}"],
        }
    finally:
        if not save_json:
            try:
                Path(json_path).unlink(missing_ok=True)
            except Exception:
                pass


def launch_agent_session(persona: str = "don_trabajo", mode: str = "local") -> None:
    """
    Launch an interactive agent session (blocking).

    Args:
        persona: Persona name (currently informational).
        mode: Backend mode ("local" supported).
    """
    if mode != "local":
        return
    try:
        load_dotenv(dotenv_path="tools/agent/.env", override=False)
        from tools.agent import runner

        runner.repl()
    except Exception:
        return


def agent_one_shot(query: str, persona: str = "don_trabajo", mode: str = "local") -> dict:
    """
    Execute a single agent query without a full REPL.

    Args:
        query: User prompt.
        persona: Persona name (informational).
        mode: Backend mode ("local" supported).

    Returns:
        Dict with status, response text, and error (if any).
    """
    if mode != "local":
        return {"status": "error", "response": None, "error": "Unsupported mode"}
    try:
        load_dotenv(dotenv_path="tools/agent/.env", override=False)
        from tools.agent.agent.chain import Agent

        agent = Agent.from_env()
        answer = agent.run(query)
        return {"status": "success", "response": answer, "error": None}
    except Exception as exc:
        return {"status": "error", "response": None, "error": str(exc)}

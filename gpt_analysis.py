import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from openai import OpenAI

# Load .env BEFORE using the key
load_dotenv()
console = Console()


def _get_client():
    """Lazily create an OpenAI-compatible client; return None if missing config."""
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    if not api_key:
        console.print("[red]✗ OPENAI_API_KEY not set; skipping GPT analysis.[/red]")
        return None
    try:
        return OpenAI(api_key=api_key, base_url=base_url)
    except Exception as exc:
        console.print(f"[red]✗ Failed to initialize OpenAI client: {exc}[/red]")
        return None


def format_prompt(parsed_data):
    users = parsed_data.get("users", [])
    suids = parsed_data.get("suid_binaries", [])
    kernel = parsed_data.get("kernel", {})
    ips = parsed_data.get("ip_addresses", [])
    binaries = parsed_data.get("binaries", [])

    prompt = f"""
    You're Don Trabajo GPT, a slick-talking red team assistant from the school of hard hacks.
    Provide a summary of potential privilege escalation or exploitation paths based on this data.
    Keep it tight, clear, and insightful - and drop knowledge like Prox.

    Users: {users}
    SUID Binaries: {suids}
    Kernel Info: {kernel}
    IPs: {ips}
    Binaries: {binaries}

    Drop the real: what should I check, try, or pop first?
    """
    return prompt


def run_gpt_analysis(parsed_data):
    prompt = format_prompt(parsed_data)
    client = _get_client()
    if not client:
        return

    try:
        response = client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-3.5-turbo"),
            messages=[
                {"role": "system", "content": "You are a red team operations assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=700,
        )

        output = response.choices[0].message.content
        console.print(Panel(output.strip(), title="🔎 GPT Exploitation Strategy", border_style="bright_blue"))

    except Exception as e:
        console.print(f"[red]✗ GPT request failed: {e}[/red]")

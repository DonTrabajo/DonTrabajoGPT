import os
import json
from rich.console import Console
from rich.panel import Panel
from linpeas_preprocessor import preprocess_linpeas_output
from linpeas_parser import parse_linpeas_output
from linpeas_summarizer import summarize_linpeas_findings
from cve_matcher import run_cve_matcher
from gpt_analysis import run_gpt_analysis

console = Console()

def analyze_linpeas_full_stack(raw_txt_path):
    # Step 1: Preprocess
    json_path = "temp_linpeas.json"
    console.print(Panel("[bold magenta]🔍 Starting Full Stack linPEAS Analysis[/bold magenta]", border_style="bright_magenta"))
    preprocess_linpeas_output(raw_txt_path, json_path)

    # Step 2: Parse
    console.print(Panel("[bold cyan]📊 Parsed Summary[/bold cyan]", border_style="bright_cyan"))
    parse_linpeas_output(json_path)

    # Step 3: Enrich with CVE Matching
    console.print(Panel("[bold yellow]🎯 CVE Matcher Results[/bold yellow]", border_style="yellow"))
    run_cve_matcher(json_path)

    # Step 4: GPT-style Summary
    console.print(Panel("[bold blue]🧠 Expert Recommendations[/bold blue]", border_style="blue"))
    with open(json_path, "r") as f:
        parsed = json.load(f)
    run_gpt_analysis(parsed)

    # Optional cleanup
    os.remove(json_path)

# Optional CLI use
if __name__ == "__main__":
    from sys import argv
    if len(argv) != 2:
        console.print("[red]Usage: python combo_linpeas_analyzer.py <linpeas_output.txt>[/red]")
    else:
        analyze_linpeas_full_stack(argv[1])

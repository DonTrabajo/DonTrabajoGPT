import json
import os

def validate_tool_paths():
    print("\n[+] Validating tool paths...")
    try:
        with open("tool_paths.json", "r") as file:
            tools = json.load(file)
            for name, path in tools.items():
                exists = os.path.isfile(path)
                status = "✅" if exists else "❌"
                print(f"{status} {name}: {path}")
    except FileNotFoundError:
        print("[-] tool_paths.json not found.")

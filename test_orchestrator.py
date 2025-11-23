import orchestrator


def main():
    status = orchestrator.get_llm_status()
    print("LLM status:", status)

    pre = orchestrator.preprocess_only("sample_linpeas.txt")
    print("Preprocess:", pre.get("status"), pre.get("json_path"))

    full = orchestrator.analyze_linpeas("sample_linpeas.txt", mode="none", save_json=False)
    print("Analyze status:", full.get("status"))
    print("Parsed keys:", list((full.get("parsed_data") or {}).keys()))


if __name__ == "__main__":
    main()

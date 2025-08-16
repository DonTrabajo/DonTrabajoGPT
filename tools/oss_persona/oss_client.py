import os, json, requests

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
MODEL       = os.environ.get("OSS_MODEL", "gpt-oss:20b")
TEMPERATURE = float(os.environ.get("OSS_TEMPERATURE", 0.3))
NUM_CTX     = int(os.environ.get("OSS_NUM_CTX", 8192))

def chat(messages, stream=False, timeout=(10, None)):
    url = f"{OLLAMA_HOST}/api/chat"
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": stream,
        "options": {"temperature": TEMPERATURE, "num_ctx": NUM_CTX}
    }
    if stream:
        with requests.post(url, json=payload, stream=True, timeout=timeout) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line: continue
                chunk = json.loads(line.decode("utf-8"))
                yield chunk
    else:
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
        return r.json()["message"]["content"]

def quick_answer(prompt, system=None):
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})
    return chat(msgs, stream=False)

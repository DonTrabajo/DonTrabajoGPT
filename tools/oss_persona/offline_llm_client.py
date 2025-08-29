import os, requests
from typing import List, Dict
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

BASE_URL = os.getenv("OPENAI_BASE_URL","http://127.0.0.1:11434/v1")
API_KEY  = os.getenv("OPENAI_API_KEY","ollama")
MODEL    = os.getenv("LLM_MODEL","llama3.1-local")

def chat(messages: List[Dict], temperature: float = 0.2) -> str:
    if OpenAI:
        client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
        r = client.chat.completions.create(model=MODEL, messages=messages, temperature=temperature)
        return r.choices[0].message.content
    url = f"{BASE_URL}/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type":"application/json"}
    payload = {"model": MODEL, "messages": messages, "temperature": temperature}
    resp = requests.post(url, json=payload, headers=headers, timeout=120)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

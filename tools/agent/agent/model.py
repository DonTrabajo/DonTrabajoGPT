import os, requests
from typing import List, Dict

class OllamaChat:
    def __init__(self, model: str, base_url: str | None = None, temperature: float = 0.2, num_ctx: int = 16384, timeout: int | None = None, keep_alive: str | None = None):
        self.model = model
        self.timeout = timeout or int(os.getenv('OLLAMA_TIMEOUT', '480'))
        self.keep_alive = keep_alive or os.getenv('OLLAMA_KEEP_ALIVE', '10m')
        self.base = (base_url or os.getenv("OLLAMA_BASE") or "http://localhost:11434").rstrip("/")
        self.temperature = float(temperature)
        self.num_ctx = int(num_ctx)

    def chat(self, messages: List[Dict[str, str]]) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_ctx": self.num_ctx
            }
        }
        url = f"{self.base}/api/chat"
        try:
            r = requests.post(url, json=payload, timeout=self.timeout)
        except requests.exceptions.ReadTimeout:
            # Fallback to /api/generate on timeout
            text = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            gen_payload = {
                'model': self.model,
                'prompt': text,
                'stream': False,
                'keep_alive': self.keep_alive,
                'options': {'temperature': self.temperature, 'num_ctx': self.num_ctx}
            }
            r = requests.post(f"{self.base}/api/generate", json=gen_payload, timeout=self.timeout)
            r.raise_for_status()
            data = r.json()
            return data.get('response', '')
        if r.status_code == 404:
            # fallback to /api/generate
            text = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            gen_payload = {
                "model": self.model,
                "prompt": text,
                "stream": False,
                "options": {"temperature": self.temperature, "num_ctx": self.num_ctx}
            }
            r = requests.post(f"{self.base}/api/generate", json=gen_payload, timeout=120)
            r.raise_for_status()
            data = r.json()
            return data.get("response", "")
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict) and "message" in data and isinstance(data["message"], dict):
            return data["message"].get("content", "")
        return data.get("response", "")

try:
    from ddgs import DDGS
except ImportError:  # fallback for old package name
    from duckduckgo_search import DDGS

import requests, trafilatura
import warnings
from bs4 import BeautifulSoup

def search(query: str, max_results: int = 5):
    """Return a list of search results: [{title, href, snippet}]"""
    out = []
    warnings.filterwarnings('ignore', category=RuntimeWarning);
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results or 5, safesearch='off'):
            out.append({"title": r.get("title"), "href": r.get("href"), "snippet": r.get("body")})
    return out

def get(url: str, max_chars: int = 50000):
    """Fetch a URL and return clean text (best-effort)."""
    r = requests.get(url, timeout=20, headers={"User-Agent": "OSSAgent/1.0"})
    r.raise_for_status()
    raw = r.text
    text = trafilatura.extract(raw, include_comments=False, include_tables=False) or ""
    text = text.strip()
    if len(text) > (max_chars or 50000):
        text = text[:max_chars] + "\n...[truncated]"
    return {"url": url, "text": text}

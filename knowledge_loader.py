"""
Loader utilities for the operator knowledgebase.

Provides helpers to locate the knowledgebase root, read the YAML index, resolve
topics, and fetch note content for use by orchestrators or agents. All
functions return data structures and do not perform any console I/O except in
the guarded example block.
"""

import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

import yaml


logger = logging.getLogger(__name__)

_DEFAULT_MAX_NOTE_MB = 10.0
_DEFAULT_MAX_DEPTH = 50

__all__ = [
    "get_kb_root",
    "load_index",
    "resolve_topic",
    "load_note_content",
    "get_note",
    "search_by_tag",
    "search_by_keyword",
]


def get_kb_root() -> Path:
    """Return the filesystem path to the proxoffensive-operator-knowledgebase repo.

    Prefers the PROX_KB_ROOT environment variable when set; otherwise probes
    common locations relative to this file and the user's home.

    Returns:
        Path to the knowledgebase root directory.

    Raises:
        FileNotFoundError: If no valid knowledgebase root with knowledge_index.yaml is found.
    """
    candidates: List[Path] = []
    env_path = os.getenv("PROX_KB_ROOT")
    if env_path:
        candidates.append(Path(env_path))

    current_dir = Path(__file__).resolve().parent
    candidates.extend(
        [
            current_dir / "knowledgebase",
            current_dir.parent / "proxoffensive-operator-knowledgebase",
            Path.home() / ".dontrabajogpt" / "knowledgebase",
        ]
    )

    tried: List[str] = []
    for candidate in candidates:
        index_path = candidate / "knowledge_index.yaml"
        tried.append(str(candidate))
        if candidate.is_dir() and index_path.is_file():
            return candidate

    message = (
        "Knowledgebase root not found. Tried: "
        f"{', '.join(tried)}. Set PROX_KB_ROOT to the knowledgebase path."
    )
    raise FileNotFoundError(message)


@lru_cache(maxsize=1)
def load_index() -> Dict[str, Any]:
    """Load and return the knowledge_index.yaml as a nested dict.

    Returns:
        Parsed YAML as a dict.

    Raises:
        FileNotFoundError: If the index file does not exist.
        ValueError: If YAML cannot be parsed or is not a dictionary.
    """
    index_path = get_kb_root() / "knowledge_index.yaml"
    if not index_path.is_file():
        raise FileNotFoundError(f"Knowledge index not found at {index_path}")
    try:
        with index_path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except yaml.YAMLError as exc:
        raise ValueError(f"Failed to parse YAML: {exc}") from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError("Parsed knowledge index must be a dictionary.")
    return data


def resolve_topic(index: Dict[str, Any], topic: str) -> Optional[Dict[str, Any]]:
    """Resolve a dotted topic string into an index node.

    Args:
        index: Parsed knowledge index.
        topic: Dotted path into the index (e.g., 'htb.pivoting.socks5_rdp_lab').

    Returns:
        The leaf node dict if found, otherwise None.
    """
    if not topic or not isinstance(topic, str):
        return None
    node: Any = index
    for key in [part for part in topic.split(".") if part]:
        if not isinstance(node, dict) or key not in node:
            return None
        node = node[key]
    return node if _is_leaf(node) else None


def load_note_content(note_entry: Dict[str, Any], max_size_mb: float = _DEFAULT_MAX_NOTE_MB) -> str:
    """Load the markdown content of a note from the knowledgebase.

    Args:
        note_entry: A leaf entry from the index that includes a 'path' key.
        max_size_mb: Maximum allowed file size in megabytes.

    Returns:
        The note content as a string.

    Raises:
        FileNotFoundError: If the note file does not exist.
        KeyError: If 'path' is missing from the entry.
        ValueError: If the note path escapes the knowledgebase root or exceeds the size limit.
    """
    if "path" not in note_entry:
        raise KeyError("'path' is missing from the note entry")
    kb_root = get_kb_root().resolve()
    note_path = (kb_root / note_entry["path"]).resolve()
    try:
        note_path.relative_to(kb_root)
    except ValueError as exc:
        raise ValueError(f"Path traversal detected: {note_path}") from exc
    if not note_path.is_file():
        raise FileNotFoundError(f"Note file not found at {note_path}")
    size_mb = note_path.stat().st_size / (1024 * 1024)
    if size_mb > max_size_mb:
        raise ValueError(f"Note file too large ({size_mb:.2f} MB), limit is {max_size_mb:.2f} MB")
    try:
        return note_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"Failed to decode note content at {note_path}: {exc}") from exc


def get_note(topic: str) -> Optional[Dict[str, Any]]:
    """High-level helper: load index, resolve topic, and attach note content.

    Args:
        topic: Dotted topic path (e.g., 'htb.pivoting.socks5_rdp_lab').

    Returns:
        A dict with:
            {
                "topic": str,
                "meta": dict,        # index leaf
                "content": str
            }
        Or None if the topic cannot be resolved.
    """
    index = load_index()
    meta = resolve_topic(index, topic)
    if meta is None:
        return None
    try:
        content = load_note_content(meta)
    except (FileNotFoundError, ValueError):
        return None
    return {"topic": topic, "meta": meta, "content": content}


def _iter_leaves(index: Dict[str, Any], max_depth: int = _DEFAULT_MAX_DEPTH) -> Iterator[Tuple[str, Dict[str, Any]]]:
    """Yield dotted topic paths and metadata for each leaf node in the index."""

    def _walk(node: Any, path_parts: List[str]) -> Iterator[Tuple[str, Dict[str, Any]]]:
        if not isinstance(node, dict):
            return
        if len(path_parts) > max_depth:
            logger.warning("Maximum recursion depth reached at %s", ".".join(path_parts))
            return
        if _is_leaf(node):
            topic_path = ".".join(path_parts)
            yield topic_path, node
            return
        for key, value in node.items():
            if isinstance(value, dict):
                yield from _walk(value, path_parts + [key])

    yield from _walk(index, [])


def search_by_tag(tag: str) -> List[Dict[str, Any]]:
    """Return a list of index leaf nodes that contain the given tag.

    Each result item includes the dotted topic path and the index entry.

    Args:
        tag: Tag value to match.

    Returns:
        List of dicts shaped as {"topic": str, "meta": dict}.
    """
    index = load_index()
    results: List[Dict[str, Any]] = []
    for topic_path, meta in _iter_leaves(index):
        tags = meta.get("tags")
        tag_list = tags if isinstance(tags, list) else []
        if tag in tag_list:
            results.append({"topic": topic_path, "meta": meta})
    return results


def _is_leaf(node: Any) -> bool:
    """Return True if the node represents a leaf entry with a path."""
    return isinstance(node, dict) and "path" in node and isinstance(node.get("path"), str)


def _build_snippet(content: str, match_start: int, match_length: int, context: int = 80) -> str:
    """Return a short excerpt around the given match position."""
    snippet_start = max(0, match_start - context)
    snippet_end = min(len(content), match_start + match_length + context)
    return content[snippet_start:snippet_end].strip()


def search_by_keyword(keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Naive keyword search across note contents.

    Args:
        keyword: Substring to search for (case-insensitive).
        limit: Maximum number of results.

    Returns:
        List of results with topic, meta, and a snippet around the first match.
    """
    if limit <= 0:
        return []
    if not keyword or not isinstance(keyword, str):
        return []
    keyword = keyword.strip()
    if not keyword:
        return []
    if len(keyword) > 500:
        return []

    index = load_index()
    results: List[Dict[str, Any]] = []
    keyword_lower = keyword.lower()
    kb_root = get_kb_root().resolve()

    for topic_path, meta in _iter_leaves(index):
        note_path = meta.get("path")
        if not isinstance(note_path, str):
            continue
        full_path = (kb_root / note_path).resolve()
        try:
            full_path.relative_to(kb_root)
        except ValueError:
            logger.warning("Path traversal blocked for topic '%s': %s", topic_path, full_path)
            continue
        try:
            size_mb = full_path.stat().st_size / (1024 * 1024)
            if size_mb > _DEFAULT_MAX_NOTE_MB:
                logger.debug(
                    "Skipping note for topic '%s' due to size %.2f MB exceeding limit %.2f MB",
                    topic_path,
                    size_mb,
                    _DEFAULT_MAX_NOTE_MB,
                )
                continue
            content = full_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            logger.debug("Note file missing for topic '%s': %s", topic_path, full_path)
            continue
        except UnicodeDecodeError as exc:
            logger.warning("Invalid encoding for topic '%s': %s", topic_path, exc)
            continue
        except OSError as exc:
            logger.warning("Failed to read note for topic '%s': %s", topic_path, exc)
            continue

        match_pos = content.lower().find(keyword_lower)
        if match_pos != -1:
            snippet = _build_snippet(content, match_pos, len(keyword))
            results.append({"topic": topic_path, "meta": meta, "snippet": snippet})
        if len(results) >= limit:
            break

    return results


if __name__ == "__main__":
    # Simple manual test: print the pivoting lab note topic if available
    try:
        note = get_note("htb.pivoting.socks5_rdp_lab")
        if note is None:
            print("Topic not found in index.")
        else:
            print(f"Loaded topic: {note['topic']}")
            print(f"Status: {note['meta'].get('status')}")
            print(note["content"][:200])
    except Exception as exc:
        print(f"Error while loading knowledge: {exc}")

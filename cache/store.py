import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List

# cache directory (~/.kaizen/cache by default)
DEFAULT_CACHE_DIR = Path.home() / ".kaizen" / "cache"
LOCAL_CACHE_DIR = Path.cwd() / ".kaizen" / "cache"


def _cache_dir() -> Path:
    override = os.environ.get("KAIZEN_CACHE_DIR")
    if override:
        return Path(override).expanduser()

    for candidate in (DEFAULT_CACHE_DIR, LOCAL_CACHE_DIR):
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            if os.access(candidate, os.W_OK):
                return candidate
        except OSError:
            continue

    return LOCAL_CACHE_DIR


def _ensure_cache_dir() -> Path:
    cache_dir = _cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _cache_file(query: str) -> Path:
    cache_dir = _ensure_cache_dir()
    safe = query.lower().replace(" ", "_")
    return cache_dir / f"{safe}.json"


def get_cache(query: str) -> Optional[Dict[str, Any]]:
    """
    Load cached result from disk
    """
    file_path = _cache_file(query)

    if not file_path.exists():
        return None

    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception:
        return None


def save_cache(query: str, data: Dict[str, Any]):
    """
    Save result to disk cache
    """
    file_path = _cache_file(query)

    payload = {
        "query": query,
        "data": data,
    }

    with open(file_path, "w") as f:
        json.dump(payload, f, indent=2)


def list_cache() -> List[str]:
    """
    List cached queries
    """
    cache_dir = _ensure_cache_dir()

    items = []

    for file in cache_dir.glob("*.json"):
        items.append(file.stem)

    return sorted(items)


def clear_cache():
    """
    Remove all cache files
    """
    cache_dir = _ensure_cache_dir()

    for file in cache_dir.glob("*.json"):
        file.unlink()

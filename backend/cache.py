"""Tiny file-based JSON cache with TTL, used to avoid re-scraping screener.in
on every request and to stay polite to the upstream site."""
import hashlib
import json
import os
import time

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

DEFAULT_TTL_SECONDS = int(os.environ.get("CACHE_TTL_SECONDS", 60 * 60 * 6))  # 6h


def _key_to_path(key: str) -> str:
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return os.path.join(CACHE_DIR, f"{digest}.json")


def get(key: str, ttl_seconds: int = DEFAULT_TTL_SECONDS):
    path = _key_to_path(key)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None
    if time.time() - payload.get("ts", 0) > ttl_seconds:
        return None
    return payload.get("data")


def set(key: str, data) -> None:
    path = _key_to_path(key)
    payload = {"ts": time.time(), "data": data}
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    os.replace(tmp_path, path)

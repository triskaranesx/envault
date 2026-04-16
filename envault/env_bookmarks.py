"""Bookmark management for envault vault entries."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any


def _bookmarks_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".bookmarks.json"


def _load_bookmarks(vault_dir: str) -> Dict[str, Any]:
    p = _bookmarks_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_bookmarks(vault_dir: str, data: Dict[str, Any]) -> None:
    _bookmarks_path(vault_dir).write_text(json.dumps(data, indent=2))


def add_bookmark(vault_dir: str, label: str, note: str = "") -> None:
    if not label:
        raise ValueError("label must not be empty")
    bm = _load_bookmarks(vault_dir)
    bm[label] = {"note": note}
    _save_bookmarks(vault_dir, bm)


def remove_bookmark(vault_dir: str, label: str) -> bool:
    bm = _load_bookmarks(vault_dir)
    if label not in bm:
        return False
    del bm[label]
    _save_bookmarks(vault_dir, bm)
    return True


def get_bookmark(vault_dir: str, label: str) -> Dict[str, Any] | None:
    return _load_bookmarks(vault_dir).get(label)


def list_bookmarks(vault_dir: str) -> Dict[str, Any]:
    return _load_bookmarks(vault_dir)


def is_bookmarked(vault_dir: str, label: str) -> bool:
    return label in _load_bookmarks(vault_dir)

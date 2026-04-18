"""Per-label inline comments stored alongside the vault."""
from __future__ import annotations
import json
from pathlib import Path


def _comments_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".envault_comments.json"


def _load_comments(vault_dir: str) -> dict:
    p = _comments_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_comments(vault_dir: str, data: dict) -> None:
    _comments_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_comment(vault_dir: str, label: str, comment: str) -> None:
    if not label:
        raise ValueError("label must not be empty")
    if not comment:
        raise ValueError("comment must not be empty")
    data = _load_comments(vault_dir)
    data[label] = comment.strip()
    _save_comments(vault_dir, data)


def get_comment(vault_dir: str, label: str) -> str | None:
    return _load_comments(vault_dir).get(label)


def remove_comment(vault_dir: str, label: str) -> bool:
    data = _load_comments(vault_dir)
    if label not in data:
        return False
    del data[label]
    _save_comments(vault_dir, data)
    return True


def list_comments(vault_dir: str) -> dict:
    return _load_comments(vault_dir)

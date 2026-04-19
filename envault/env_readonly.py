"""Read-only flag support for vault entries."""

import json
from pathlib import Path

_READONLY_FILE = "readonly.json"


class ReadOnlyError(Exception):
    pass


def _readonly_path(vault_dir: str) -> Path:
    return Path(vault_dir) / _READONLY_FILE


def _load_readonly(vault_dir: str) -> dict:
    p = _readonly_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_readonly(vault_dir: str, data: dict) -> None:
    _readonly_path(vault_dir).write_text(json.dumps(data, indent=2))


def mark_readonly(vault_dir: str, label: str) -> None:
    if not label:
        raise ValueError("label must not be empty")
    data = _load_readonly(vault_dir)
    data[label] = True
    _save_readonly(vault_dir, data)


def unmark_readonly(vault_dir: str, label: str) -> None:
    if not label:
        raise ValueError("label must not be empty")
    data = _load_readonly(vault_dir)
    data.pop(label, None)
    _save_readonly(vault_dir, data)


def is_readonly(vault_dir: str, label: str) -> bool:
    return _load_readonly(vault_dir).get(label, False)


def list_readonly(vault_dir: str) -> list:
    return [k for k, v in _load_readonly(vault_dir).items() if v]


def assert_writable(vault_dir: str, label: str) -> None:
    if is_readonly(vault_dir, label):
        raise ReadOnlyError(f"Entry '{label}' is marked read-only")

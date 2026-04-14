"""env_defaults.py – Store and retrieve default values for vault entries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

_DEFAULTS_FILE = "defaults.json"


def _defaults_path(vault_dir: str) -> Path:
    return Path(vault_dir) / _DEFAULTS_FILE


def _load_defaults(vault_dir: str) -> Dict[str, str]:
    path = _defaults_path(vault_dir)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_defaults(vault_dir: str, data: Dict[str, str]) -> None:
    path = _defaults_path(vault_dir)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def set_default(vault_dir: str, label: str, value: str) -> None:
    """Set or overwrite the default value for *label*."""
    if not label:
        raise ValueError("label must not be empty")
    data = _load_defaults(vault_dir)
    data[label] = value
    _save_defaults(vault_dir, data)


def get_default(vault_dir: str, label: str) -> Optional[str]:
    """Return the default value for *label*, or None if not set."""
    return _load_defaults(vault_dir).get(label)


def remove_default(vault_dir: str, label: str) -> bool:
    """Remove the default for *label*.  Returns True if it existed."""
    data = _load_defaults(vault_dir)
    if label not in data:
        return False
    del data[label]
    _save_defaults(vault_dir, data)
    return True


def list_defaults(vault_dir: str) -> Dict[str, str]:
    """Return a copy of all stored defaults."""
    return dict(_load_defaults(vault_dir))


def clear_defaults(vault_dir: str) -> int:
    """Remove all defaults.  Returns the number of entries cleared."""
    data = _load_defaults(vault_dir)
    count = len(data)
    _save_defaults(vault_dir, {})
    return count

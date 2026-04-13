"""
envault/aliases.py — Manage short aliases for vault entry labels.

Allows users to define friendly shorthand names that map to full labels,
making it easier to retrieve commonly used secrets.
"""

import json
from pathlib import Path

_ALIASES_FILE = "aliases.json"


def _load_aliases(vault_dir: str) -> dict:
    path = Path(vault_dir) / _ALIASES_FILE
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_aliases(vault_dir: str, data: dict) -> None:
    path = Path(vault_dir) / _ALIASES_FILE
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_alias(vault_dir: str, alias: str, label: str) -> None:
    """Create or overwrite an alias pointing to a label."""
    if not alias or not label:
        raise ValueError("alias and label must be non-empty strings")
    data = _load_aliases(vault_dir)
    data[alias] = label
    _save_aliases(vault_dir, data)


def get_alias(vault_dir: str, alias: str) -> str | None:
    """Return the label for a given alias, or None if not found."""
    data = _load_aliases(vault_dir)
    return data.get(alias)


def remove_alias(vault_dir: str, alias: str) -> bool:
    """Remove an alias. Returns True if it existed, False otherwise."""
    data = _load_aliases(vault_dir)
    if alias not in data:
        return False
    del data[alias]
    _save_aliases(vault_dir, data)
    return True


def list_aliases(vault_dir: str) -> dict:
    """Return all alias -> label mappings."""
    return _load_aliases(vault_dir)


def resolve(vault_dir: str, alias_or_label: str) -> str:
    """Resolve an alias to its label; return input unchanged if not an alias."""
    resolved = get_alias(vault_dir, alias_or_label)
    return resolved if resolved is not None else alias_or_label

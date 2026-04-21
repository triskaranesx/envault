"""Visibility control for vault entries (public / private / masked)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

VALID_LEVELS = ("public", "private", "masked")


class VisibilityError(ValueError):
    pass


def _visibility_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".visibility.json"


def _load_visibility(vault_dir: str) -> Dict[str, str]:
    p = _visibility_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_visibility(vault_dir: str, data: Dict[str, str]) -> None:
    _visibility_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_visibility(vault_dir: str, label: str, level: str) -> None:
    """Set the visibility level for *label*."""
    if not label:
        raise VisibilityError("label must not be empty")
    if level not in VALID_LEVELS:
        raise VisibilityError(
            f"invalid level {level!r}; choose from {VALID_LEVELS}"
        )
    data = _load_visibility(vault_dir)
    data[label] = level
    _save_visibility(vault_dir, data)


def get_visibility(vault_dir: str, label: str) -> Optional[str]:
    """Return the visibility level for *label*, or None if not set."""
    return _load_visibility(vault_dir).get(label)


def remove_visibility(vault_dir: str, label: str) -> bool:
    """Remove visibility setting for *label*. Returns True if it existed."""
    data = _load_visibility(vault_dir)
    if label not in data:
        return False
    del data[label]
    _save_visibility(vault_dir, data)
    return True


def list_visibility(vault_dir: str) -> List[Dict[str, str]]:
    """Return all visibility settings as a list of dicts."""
    data = _load_visibility(vault_dir)
    return [{"label": k, "level": v} for k, v in sorted(data.items())]


def filter_by_level(vault_dir: str, level: str) -> List[str]:
    """Return labels whose visibility matches *level*."""
    if level not in VALID_LEVELS:
        raise VisibilityError(
            f"invalid level {level!r}; choose from {VALID_LEVELS}"
        )
    data = _load_visibility(vault_dir)
    return [label for label, lv in sorted(data.items()) if lv == level]

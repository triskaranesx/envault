"""Sensitivity levels for vault entries (e.g. low, medium, high, critical)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

VALID_LEVELS = ("low", "medium", "high", "critical")


class SensitivityError(ValueError):
    pass


def _sensitivity_path(vault_dir: str) -> Path:
    return Path(vault_dir) / "sensitivity.json"


def _load_sensitivity(vault_dir: str) -> Dict[str, str]:
    path = _sensitivity_path(vault_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_sensitivity(vault_dir: str, data: Dict[str, str]) -> None:
    _sensitivity_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_sensitivity(vault_dir: str, label: str, level: str) -> str:
    """Assign a sensitivity level to a label. Returns the stored level."""
    if not label:
        raise SensitivityError("label must not be empty")
    level = level.lower()
    if level not in VALID_LEVELS:
        raise SensitivityError(
            f"invalid level {level!r}; choose from {VALID_LEVELS}"
        )
    data = _load_sensitivity(vault_dir)
    data[label] = level
    _save_sensitivity(vault_dir, data)
    return level


def get_sensitivity(vault_dir: str, label: str) -> Optional[str]:
    """Return the sensitivity level for *label*, or None if not set."""
    return _load_sensitivity(vault_dir).get(label)


def remove_sensitivity(vault_dir: str, label: str) -> bool:
    """Remove the sensitivity record for *label*. Returns True if it existed."""
    data = _load_sensitivity(vault_dir)
    if label not in data:
        return False
    del data[label]
    _save_sensitivity(vault_dir, data)
    return True


def list_sensitivity(vault_dir: str) -> List[Dict[str, str]]:
    """Return all sensitivity records sorted by label."""
    data = _load_sensitivity(vault_dir)
    return [
        {"label": lbl, "level": lvl}
        for lbl, lvl in sorted(data.items())
    ]


def filter_by_level(vault_dir: str, level: str) -> List[str]:
    """Return labels whose sensitivity matches *level*."""
    level = level.lower()
    data = _load_sensitivity(vault_dir)
    return sorted(lbl for lbl, lvl in data.items() if lvl == level)

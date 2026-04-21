"""Track which vault labels are marked as required."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional


class RequiredError(Exception):
    """Raised when an operation violates a required-field constraint."""


def _required_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".envault_required.json"


def _load_required(vault_dir: str) -> List[str]:
    p = _required_path(vault_dir)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save_required(vault_dir: str, labels: List[str]) -> None:
    _required_path(vault_dir).write_text(json.dumps(sorted(set(labels)), indent=2))


def mark_required(vault_dir: str, label: str) -> None:
    """Mark *label* as required."""
    if not label or not label.strip():
        raise RequiredError("Label must not be empty.")
    labels = _load_required(vault_dir)
    if label not in labels:
        labels.append(label)
    _save_required(vault_dir, labels)


def unmark_required(vault_dir: str, label: str) -> bool:
    """Remove the required flag from *label*. Returns True if it was present."""
    labels = _load_required(vault_dir)
    if label in labels:
        labels.remove(label)
        _save_required(vault_dir, labels)
        return True
    return False


def is_required(vault_dir: str, label: str) -> bool:
    """Return True if *label* is marked as required."""
    return label in _load_required(vault_dir)


def list_required(vault_dir: str) -> List[str]:
    """Return all labels currently marked as required."""
    return _load_required(vault_dir)


def check_required(vault_dir: str, present_labels: List[str]) -> List[str]:
    """Return required labels that are absent from *present_labels*."""
    required = set(_load_required(vault_dir))
    present = set(present_labels)
    return sorted(required - present)

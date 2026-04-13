"""Per-entry notes/comments stored alongside vault entries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

_NOTES_FILE = "notes.json"


def _load_notes(vault_dir: str) -> Dict[str, str]:
    path = Path(vault_dir) / _NOTES_FILE
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_notes(vault_dir: str, data: Dict[str, str]) -> None:
    path = Path(vault_dir) / _NOTES_FILE
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def set_note(vault_dir: str, label: str, note: str) -> None:
    """Attach a plaintext note to a vault entry label."""
    if not label:
        raise ValueError("label must not be empty")
    data = _load_notes(vault_dir)
    data[label] = note
    _save_notes(vault_dir, data)


def get_note(vault_dir: str, label: str) -> Optional[str]:
    """Return the note for *label*, or None if not set."""
    return _load_notes(vault_dir).get(label)


def remove_note(vault_dir: str, label: str) -> bool:
    """Remove the note for *label*.  Returns True if a note existed."""
    data = _load_notes(vault_dir)
    if label not in data:
        return False
    del data[label]
    _save_notes(vault_dir, data)
    return True


def list_notes(vault_dir: str) -> Dict[str, str]:
    """Return a mapping of {label: note} for all entries that have notes."""
    return dict(_load_notes(vault_dir))

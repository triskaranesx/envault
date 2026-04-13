"""Version history management for vault entries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

HISTORY_FILE = ".envault_history.json"


def _load_history(vault_dir: str = ".") -> dict:
    path = Path(vault_dir) / HISTORY_FILE
    if not path.exists():
        return {"entries": []}
    with open(path, "r") as f:
        return json.load(f)


def _save_history(data: dict, vault_dir: str = ".") -> None:
    path = Path(vault_dir) / HISTORY_FILE
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def record_change(
    label: str,
    version: int,
    action: str,
    actor: str = "local",
    vault_dir: str = ".",
) -> None:
    """Append a change record to the history log."""
    import datetime

    history = _load_history(vault_dir)
    history["entries"].append(
        {
            "label": label,
            "version": version,
            "action": action,
            "actor": actor,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        }
    )
    _save_history(history, vault_dir)


def get_history(label: str | None = None, vault_dir: str = ".") -> list[dict[str, Any]]:
    """Return history records, optionally filtered by label."""
    history = _load_history(vault_dir)
    entries = history["entries"]
    if label is not None:
        entries = [e for e in entries if e["label"] == label]
    return entries


def clear_history(vault_dir: str = ".") -> None:
    """Wipe all history records."""
    _save_history({"entries": []}, vault_dir)

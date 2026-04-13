"""Snapshot management: save and restore named vault snapshots."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

_SNAPSHOTS_FILE = "snapshots.json"


def _snapshots_path(vault_dir: str) -> Path:
    return Path(vault_dir) / _SNAPSHOTS_FILE


def _load_snapshots(vault_dir: str) -> dict:
    p = _snapshots_path(vault_dir)
    if not p.exists():
        return {}
    with open(p, "r") as f:
        return json.load(f)


def _save_snapshots(vault_dir: str, data: dict) -> None:
    p = _snapshots_path(vault_dir)
    with open(p, "w") as f:
        json.dump(data, f, indent=2)


def save_snapshot(vault_dir: str, name: str) -> str:
    """Save the current vault state as a named snapshot.
    Returns the ISO timestamp of the snapshot."""
    if not name or not name.strip():
        raise ValueError("Snapshot name must not be empty.")

    vault_file = Path(vault_dir) / "vault.json"
    if not vault_file.exists():
        raise FileNotFoundError(f"No vault found at {vault_dir}")

    with open(vault_file, "r") as f:
        vault_data = json.load(f)

    snapshots = _load_snapshots(vault_dir)
    ts = datetime.now(timezone.utc).isoformat()
    snapshots[name] = {
        "created_at": ts,
        "vault": vault_data,
    }
    _save_snapshots(vault_dir, snapshots)
    return ts


def get_snapshot(vault_dir: str, name: str) -> dict | None:
    """Return snapshot data for the given name, or None if not found."""
    snapshots = _load_snapshots(vault_dir)
    return snapshots.get(name)


def list_snapshots(vault_dir: str) -> list[dict]:
    """Return a list of snapshot summaries sorted by creation time."""
    snapshots = _load_snapshots(vault_dir)
    result = [
        {"name": name, "created_at": info["created_at"]}
        for name, info in snapshots.items()
    ]
    return sorted(result, key=lambda x: x["created_at"])


def restore_snapshot(vault_dir: str, name: str) -> int:
    """Restore vault from a named snapshot.
    Returns the number of entries restored."""
    snapshot = get_snapshot(vault_dir, name)
    if snapshot is None:
        raise KeyError(f"Snapshot '{name}' not found.")

    vault_data = snapshot["vault"]
    vault_file = Path(vault_dir) / "vault.json"
    with open(vault_file, "w") as f:
        json.dump(vault_data, f, indent=2)

    return len(vault_data.get("entries", []))


def delete_snapshot(vault_dir: str, name: str) -> bool:
    """Delete a named snapshot. Returns True if deleted, False if not found."""
    snapshots = _load_snapshots(vault_dir)
    if name not in snapshots:
        return False
    del snapshots[name]
    _save_snapshots(vault_dir, snapshots)
    return True

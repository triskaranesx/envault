"""Archive (soft-delete) and restore vault entries."""
import json
from pathlib import Path
from typing import List, Optional

_ARCHIVE_FILE = ".archive.json"


def _archive_path(vault_dir: str) -> Path:
    return Path(vault_dir) / _ARCHIVE_FILE


def _load_archive(vault_dir: str) -> dict:
    p = _archive_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_archive(vault_dir: str, data: dict) -> None:
    _archive_path(vault_dir).write_text(json.dumps(data, indent=2))


def archive_entry(vault_dir: str, label: str, entry: dict) -> None:
    """Move an entry to the archive store."""
    if not label:
        raise ValueError("label must not be empty")
    data = _load_archive(vault_dir)
    data[label] = entry
    _save_archive(vault_dir, data)


def restore_entry(vault_dir: str, label: str) -> dict:
    """Remove an entry from the archive and return it."""
    data = _load_archive(vault_dir)
    if label not in data:
        raise KeyError(f"No archived entry for label: {label}")
    entry = data.pop(label)
    _save_archive(vault_dir, data)
    return entry


def list_archived(vault_dir: str) -> List[str]:
    """Return labels of all archived entries."""
    return list(_load_archive(vault_dir).keys())


def get_archived(vault_dir: str, label: str) -> Optional[dict]:
    """Return a single archived entry or None."""
    return _load_archive(vault_dir).get(label)


def purge_archived(vault_dir: str, label: str) -> bool:
    """Permanently delete an archived entry. Returns True if it existed."""
    data = _load_archive(vault_dir)
    if label not in data:
        return False
    del data[label]
    _save_archive(vault_dir, data)
    return True

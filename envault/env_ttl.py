"""TTL (time-to-live) support for vault entries."""
from __future__ import annotations
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

_TTL_FILE = "ttl.json"


def _ttl_path(vault_dir: str) -> Path:
    return Path(vault_dir) / _TTL_FILE


def _load_ttl(vault_dir: str) -> dict:
    p = _ttl_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_ttl(vault_dir: str, data: dict) -> None:
    _ttl_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_ttl(vault_dir: str, label: str, seconds: int) -> str:
    """Set a TTL for a label. Returns the expiry ISO timestamp."""
    if not label:
        raise ValueError("label must not be empty")
    if seconds <= 0:
        raise ValueError("seconds must be a positive integer")
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=seconds)
    iso = expires_at.isoformat()
    data = _load_ttl(vault_dir)
    data[label] = {"seconds": seconds, "expires_at": iso}
    _save_ttl(vault_dir, data)
    return iso


def get_ttl(vault_dir: str, label: str) -> Optional[dict]:
    """Return TTL record for label, or None if not set."""
    return _load_ttl(vault_dir).get(label)


def remove_ttl(vault_dir: str, label: str) -> bool:
    """Remove TTL for label. Returns True if it existed."""
    data = _load_ttl(vault_dir)
    if label in data:
        del data[label]
        _save_ttl(vault_dir, data)
        return True
    return False


def is_expired(vault_dir: str, label: str) -> bool:
    """Return True if the label's TTL has elapsed."""
    record = get_ttl(vault_dir, label)
    if record is None:
        return False
    expires_at = datetime.fromisoformat(record["expires_at"])
    return datetime.now(timezone.utc) >= expires_at


def list_expired(vault_dir: str) -> list[str]:
    """Return all labels whose TTL has elapsed."""
    data = _load_ttl(vault_dir)
    return [label for label in data if is_expired(vault_dir, label)]


def list_ttls(vault_dir: str) -> dict:
    """Return all TTL records."""
    return _load_ttl(vault_dir)

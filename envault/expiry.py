"""Entry expiry/TTL support for envault."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

EXPIRY_FILE = "expiry.json"


def _load_expiry(vault_dir: str) -> dict:
    path = Path(vault_dir) / EXPIRY_FILE
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_expiry(vault_dir: str, data: dict) -> None:
    path = Path(vault_dir) / EXPIRY_FILE
    path.write_text(json.dumps(data, indent=2))


def set_expiry(vault_dir: str, label: str, days: int) -> str:
    """Set an expiry date for a label (days from now). Returns ISO expiry string."""
    expiry = datetime.now(timezone.utc) + timedelta(days=days)
    iso = expiry.isoformat()
    data = _load_expiry(vault_dir)
    data[label] = iso
    _save_expiry(vault_dir, data)
    return iso


def get_expiry(vault_dir: str, label: str) -> Optional[str]:
    """Return ISO expiry string for label, or None if not set."""
    data = _load_expiry(vault_dir)
    return data.get(label)


def remove_expiry(vault_dir: str, label: str) -> bool:
    """Remove expiry for a label. Returns True if it existed."""
    data = _load_expiry(vault_dir)
    if label not in data:
        return False
    del data[label]
    _save_expiry(vault_dir, data)
    return True


def is_expired(vault_dir: str, label: str) -> bool:
    """Return True if the label has an expiry that has passed."""
    iso = get_expiry(vault_dir, label)
    if iso is None:
        return False
    expiry_dt = datetime.fromisoformat(iso)
    return datetime.now(timezone.utc) >= expiry_dt


def list_expired(vault_dir: str) -> list[str]:
    """Return list of labels whose expiry has passed."""
    data = _load_expiry(vault_dir)
    now = datetime.now(timezone.utc)
    return [
        label
        for label, iso in data.items()
        if datetime.fromisoformat(iso) <= now
    ]


def list_all_expiry(vault_dir: str) -> dict:
    """Return all label -> expiry ISO mappings."""
    return _load_expiry(vault_dir)

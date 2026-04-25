"""Entry status tracking: active, deprecated, experimental, stable."""

import json
from pathlib import Path

VALID_STATUSES = {"active", "deprecated", "experimental", "stable"}


class StatusError(ValueError):
    pass


def _status_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".envault_status.json"


def _load_status(vault_dir: str) -> dict:
    p = _status_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_status(vault_dir: str, data: dict) -> None:
    _status_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_status(vault_dir: str, label: str, status: str) -> str:
    """Set the status for a label. Returns the status string."""
    if not label or not label.strip():
        raise StatusError("Label must not be empty.")
    status = status.lower().strip()
    if status not in VALID_STATUSES:
        raise StatusError(
            f"Invalid status '{status}'. Must be one of: {sorted(VALID_STATUSES)}"
        )
    data = _load_status(vault_dir)
    data[label] = status
    _save_status(vault_dir, data)
    return status


def get_status(vault_dir: str, label: str) -> str | None:
    """Return the status for a label, or None if not set."""
    return _load_status(vault_dir).get(label)


def remove_status(vault_dir: str, label: str) -> bool:
    """Remove the status for a label. Returns True if it existed."""
    data = _load_status(vault_dir)
    if label not in data:
        return False
    del data[label]
    _save_status(vault_dir, data)
    return True


def list_statuses(vault_dir: str) -> dict:
    """Return all label -> status mappings."""
    return dict(_load_status(vault_dir))


def find_by_status(vault_dir: str, status: str) -> list:
    """Return all labels with the given status."""
    status = status.lower().strip()
    return [label for label, s in _load_status(vault_dir).items() if s == status]

"""Audit log module for tracking access and mutations on vault entries."""

import json
import os
from datetime import datetime, timezone
from typing import Optional

AUDIT_FILE = ".envault_audit.json"


def _load_audit(vault_path: str) -> list:
    audit_path = os.path.join(os.path.dirname(vault_path), AUDIT_FILE)
    if not os.path.exists(audit_path):
        return []
    with open(audit_path, "r") as f:
        return json.load(f)


def _save_audit(vault_path: str, entries: list) -> None:
    audit_path = os.path.join(os.path.dirname(vault_path), AUDIT_FILE)
    with open(audit_path, "w") as f:
        json.dump(entries, f, indent=2)


def record_access(
    vault_path: str,
    action: str,
    label: str,
    actor: Optional[str] = None,
    note: Optional[str] = None,
) -> dict:
    """Record an access or mutation event for a vault entry.

    Args:
        vault_path: Path to the vault file.
        action: One of 'read', 'write', 'delete', 'export', 'import'.
        label: The entry label that was accessed.
        actor: Optional identifier for who performed the action.
        note: Optional free-form note.

    Returns:
        The newly created audit entry dict.
    """
    entries = _load_audit(vault_path)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "label": label,
        "actor": actor,
        "note": note,
    }
    entries.append(entry)
    _save_audit(vault_path, entries)
    return entry


def get_audit_log(
    vault_path: str,
    label: Optional[str] = None,
    action: Optional[str] = None,
) -> list:
    """Return audit entries, optionally filtered by label and/or action."""
    entries = _load_audit(vault_path)
    if label:
        entries = [e for e in entries if e.get("label") == label]
    if action:
        entries = [e for e in entries if e.get("action") == action]
    return entries


def clear_audit_log(vault_path: str) -> None:
    """Wipe all audit log entries."""
    _save_audit(vault_path, [])

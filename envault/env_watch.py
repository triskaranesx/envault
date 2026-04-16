"""Watch a vault for changes and trigger hooks or notifications."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Callable, Optional


def _vault_fingerprint(vault_path: Path) -> str:
    """Return an MD5 hex digest of the vault file contents."""
    try:
        raw = vault_path.read_bytes()
    except FileNotFoundError:
        return ""
    return hashlib.md5(raw).hexdigest()


def _load_watch_state(vault_dir: Path) -> dict:
    state_path = vault_dir / ".watch_state.json"
    if not state_path.exists():
        return {}
    return json.loads(state_path.read_text())


def _save_watch_state(vault_dir: Path, state: dict) -> None:
    state_path = vault_dir / ".watch_state.json"
    state_path.write_text(json.dumps(state, indent=2))


def get_last_seen_fingerprint(vault_dir: Path) -> Optional[str]:
    """Return the last recorded fingerprint, or None if never watched."""
    state = _load_watch_state(vault_dir)
    return state.get("fingerprint")


def update_fingerprint(vault_dir: Path) -> str:
    """Record the current vault fingerprint and return it."""
    vault_path = vault_dir / "vault.json"
    fp = _vault_fingerprint(vault_path)
    state = _load_watch_state(vault_dir)
    state["fingerprint"] = fp
    state["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    _save_watch_state(vault_dir, state)
    return fp


def has_changed(vault_dir: Path) -> bool:
    """Return True if the vault has changed since last check."""
    vault_path = vault_dir / "vault.json"
    current = _vault_fingerprint(vault_path)
    last = get_last_seen_fingerprint(vault_dir)
    return current != last


def watch_once(
    vault_dir: Path,
    on_change: Callable[[Path], None],
) -> bool:
    """Check for a change, call on_change if detected, update state.

    Returns True if a change was detected.
    """
    changed = has_changed(vault_dir)
    if changed:
        on_change(vault_dir)
    update_fingerprint(vault_dir)
    return changed


def poll(
    vault_dir: Path,
    on_change: Callable[[Path], None],
    interval: float = 2.0,
    max_checks: Optional[int] = None,
) -> None:
    """Poll the vault repeatedly; call on_change whenever a change is detected."""
    checks = 0
    while max_checks is None or checks < max_checks:
        watch_once(vault_dir, on_change)
        checks += 1
        if max_checks is None or checks < max_checks:
            time.sleep(interval)

"""Pre/post hooks for vault operations (add, get, rotate, import)."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Optional

HOOKS_FILE = "hooks.json"

VALID_EVENTS = {"pre-add", "post-add", "pre-get", "post-get", "pre-rotate", "post-rotate"}


def _hooks_path(vault_dir: str) -> Path:
    return Path(vault_dir) / HOOKS_FILE


def _load_hooks(vault_dir: str) -> dict:
    p = _hooks_path(vault_dir)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_hooks(vault_dir: str, data: dict) -> None:
    with open(_hooks_path(vault_dir), "w") as f:
        json.dump(data, f, indent=2)


def set_hook(vault_dir: str, event: str, command: str) -> None:
    """Register a shell command to run on *event*."""
    if event not in VALID_EVENTS:
        raise ValueError(f"Unknown event '{event}'. Valid events: {sorted(VALID_EVENTS)}")
    if not command.strip():
        raise ValueError("Hook command must not be empty.")
    data = _load_hooks(vault_dir)
    data[event] = command
    _save_hooks(vault_dir, data)


def get_hook(vault_dir: str, event: str) -> Optional[str]:
    """Return the registered command for *event*, or None."""
    return _load_hooks(vault_dir).get(event)


def remove_hook(vault_dir: str, event: str) -> bool:
    """Remove the hook for *event*. Returns True if it existed."""
    data = _load_hooks(vault_dir)
    if event in data:
        del data[event]
        _save_hooks(vault_dir, data)
        return True
    return False


def list_hooks(vault_dir: str) -> dict:
    """Return all registered hooks as {event: command}."""
    return dict(_load_hooks(vault_dir))


def run_hook(vault_dir: str, event: str, env_extra: Optional[dict] = None) -> Optional[int]:
    """Execute the hook for *event* if one is registered.

    Returns the process exit code, or None if no hook is set.
    Raises RuntimeError if the hook exits with a non-zero code.
    """
    command = get_hook(vault_dir, event)
    if command is None:
        return None
    env = {**os.environ, **(env_extra or {})}
    result = subprocess.run(command, shell=True, env=env)  # noqa: S602
    if result.returncode != 0:
        raise RuntimeError(
            f"Hook '{event}' failed with exit code {result.returncode}: {command}"
        )
    return result.returncode

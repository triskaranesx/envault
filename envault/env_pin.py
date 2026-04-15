"""Pin management for envault: lock specific entries to a required value."""

import json
from pathlib import Path
from typing import Optional

_PINS_FILE = ".pins.json"


def _pins_path(vault_dir: str) -> Path:
    return Path(vault_dir) / _PINS_FILE


def _load_pins(vault_dir: str) -> dict:
    p = _pins_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_pins(vault_dir: str, pins: dict) -> None:
    _pins_path(vault_dir).write_text(json.dumps(pins, indent=2))


def pin_entry(vault_dir: str, label: str, value: str) -> None:
    """Pin a label to a specific required value."""
    if not label:
        raise ValueError("Label must not be empty.")
    if value is None:
        raise ValueError("Pin value must not be None.")
    pins = _load_pins(vault_dir)
    pins[label] = value
    _save_pins(vault_dir, pins)


def unpin_entry(vault_dir: str, label: str) -> bool:
    """Remove a pin. Returns True if it existed, False otherwise."""
    pins = _load_pins(vault_dir)
    if label in pins:
        del pins[label]
        _save_pins(vault_dir, pins)
        return True
    return False


def get_pin(vault_dir: str, label: str) -> Optional[str]:
    """Return the pinned value for a label, or None if not pinned."""
    return _load_pins(vault_dir).get(label)


def list_pins(vault_dir: str) -> dict:
    """Return all pinned labels and their required values."""
    return dict(_load_pins(vault_dir))


def check_pins(vault_dir: str, resolved: dict) -> list:
    """Check resolved key/value pairs against pins.

    Returns a list of violation dicts with keys: label, expected, actual.
    """
    pins = _load_pins(vault_dir)
    violations = []
    for label, expected in pins.items():
        actual = resolved.get(label)
        if actual != expected:
            violations.append({"label": label, "expected": expected, "actual": actual})
    return violations

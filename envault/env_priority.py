"""Priority levels for vault entries."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Optional

VALID_PRIORITIES = ("low", "normal", "high", "critical")


def _priority_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".priority.json"


def _load_priorities(vault_dir: str) -> Dict[str, str]:
    p = _priority_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_priorities(vault_dir: str, data: Dict[str, str]) -> None:
    _priority_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_priority(vault_dir: str, label: str, priority: str) -> None:
    if not label:
        raise ValueError("label must not be empty")
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"priority must be one of {VALID_PRIORITIES}")
    data = _load_priorities(vault_dir)
    data[label] = priority
    _save_priorities(vault_dir, data)


def get_priority(vault_dir: str, label: str) -> Optional[str]:
    return _load_priorities(vault_dir).get(label)


def remove_priority(vault_dir: str, label: str) -> bool:
    data = _load_priorities(vault_dir)
    if label not in data:
        return False
    del data[label]
    _save_priorities(vault_dir, data)
    return True


def list_priorities(vault_dir: str) -> List[Dict[str, str]]:
    data = _load_priorities(vault_dir)
    return [{"label": k, "priority": v} for k, v in sorted(data.items())]


def find_by_priority(vault_dir: str, priority: str) -> List[str]:
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"priority must be one of {VALID_PRIORITIES}")
    data = _load_priorities(vault_dir)
    return [label for label, p in data.items() if p == priority]

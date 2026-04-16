"""Group management for vault entries."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Optional

_GROUPS_FILE = ".envault_groups.json"


def _groups_path(vault_dir: str) -> Path:
    return Path(vault_dir) / _GROUPS_FILE


def _load_groups(vault_dir: str) -> Dict[str, List[str]]:
    p = _groups_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_groups(vault_dir: str, data: Dict[str, List[str]]) -> None:
    _groups_path(vault_dir).write_text(json.dumps(data, indent=2))


def create_group(vault_dir: str, group: str) -> None:
    if not group.strip():
        raise ValueError("Group name must not be empty.")
    data = _load_groups(vault_dir)
    if group not in data:
        data[group] = []
        _save_groups(vault_dir, data)


def delete_group(vault_dir: str, group: str) -> None:
    data = _load_groups(vault_dir)
    data.pop(group, None)
    _save_groups(vault_dir, data)


def add_label_to_group(vault_dir: str, group: str, label: str) -> None:
    if not group.strip():
        raise ValueError("Group name must not be empty.")
    data = _load_groups(vault_dir)
    members = data.setdefault(group, [])
    if label not in members:
        members.append(label)
    _save_groups(vault_dir, data)


def remove_label_from_group(vault_dir: str, group: str, label: str) -> None:
    data = _load_groups(vault_dir)
    if group in data and label in data[group]:
        data[group].remove(label)
    _save_groups(vault_dir, data)


def get_group(vault_dir: str, group: str) -> Optional[List[str]]:
    data = _load_groups(vault_dir)
    return data.get(group)


def list_groups(vault_dir: str) -> List[str]:
    return list(_load_groups(vault_dir).keys())


def find_groups_for_label(vault_dir: str, label: str) -> List[str]:
    data = _load_groups(vault_dir)
    return [g for g, members in data.items() if label in members]

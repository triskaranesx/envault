"""Namespace support for grouping env labels under logical prefixes."""

import json
from pathlib import Path

NAMESPACE_FILE = ".envault_namespaces.json"


class NamespaceError(Exception):
    pass


def _ns_path(vault_dir: str) -> Path:
    return Path(vault_dir) / NAMESPACE_FILE


def _load_namespaces(vault_dir: str) -> dict:
    p = _ns_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_namespaces(vault_dir: str, data: dict) -> None:
    _ns_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_namespace(vault_dir: str, label: str, namespace: str) -> None:
    """Assign a label to a namespace."""
    if not label:
        raise NamespaceError("Label must not be empty.")
    if not namespace or not namespace.replace("-", "").replace("_", "").isalnum():
        raise NamespaceError(f"Invalid namespace '{namespace}': use alphanumeric, hyphens, or underscores.")
    data = _load_namespaces(vault_dir)
    data[label] = namespace
    _save_namespaces(vault_dir, data)


def get_namespace(vault_dir: str, label: str) -> str | None:
    """Return the namespace for a label, or None."""
    return _load_namespaces(vault_dir).get(label)


def remove_namespace(vault_dir: str, label: str) -> bool:
    """Remove a label's namespace assignment. Returns True if removed."""
    data = _load_namespaces(vault_dir)
    if label not in data:
        return False
    del data[label]
    _save_namespaces(vault_dir, data)
    return True


def list_namespaces(vault_dir: str) -> dict:
    """Return all label -> namespace mappings."""
    return _load_namespaces(vault_dir)


def get_labels_in_namespace(vault_dir: str, namespace: str) -> list:
    """Return all labels assigned to a given namespace."""
    data = _load_namespaces(vault_dir)
    return sorted(label for label, ns in data.items() if ns == namespace)

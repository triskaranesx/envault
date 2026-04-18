"""Label management: bulk rename, list, and normalize labels in the vault."""
from __future__ import annotations
from typing import List, Dict
from envault.vault import _load_vault_raw, _save_vault_raw


class LabelError(Exception):
    pass


def list_labels(vault_path: str) -> List[str]:
    """Return all labels currently in the vault."""
    vault = _load_vault_raw(vault_path)
    return [e["label"] for e in vault.get("entries", [])]


def normalize_labels(vault_path: str) -> Dict[str, str]:
    """Uppercase all labels in-place. Returns mapping old->new."""
    vault = _load_vault_raw(vault_path)
    mapping: Dict[str, str] = {}
    for entry in vault.get("entries", []):
        old = entry["label"]
        new = old.upper()
        if old != new:
            mapping[old] = new
            entry["label"] = new
    if mapping:
        _save_vault_raw(vault_path, vault)
    return mapping


def bulk_rename_labels(vault_path: str, mapping: Dict[str, str]) -> List[str]:
    """Rename multiple labels at once. Returns list of labels that were changed."""
    if not mapping:
        raise LabelError("Mapping must not be empty.")
    vault = _load_vault_raw(vault_path)
    entries = vault.get("entries", [])
    existing = {e["label"] for e in entries}
    for old, new in mapping.items():
        if old not in existing:
            raise LabelError(f"Label '{old}' not found in vault.")
        if new in existing and new not in mapping:
            raise LabelError(f"Target label '{new}' already exists.")
    changed = []
    for entry in entries:
        if entry["label"] in mapping:
            entry["label"] = mapping[entry["label"]]
            changed.append(entry["label"])
    _save_vault_raw(vault_path, vault)
    return changed


def find_duplicate_labels(vault_path: str) -> List[str]:
    """Return labels that appear more than once (should not happen but useful for repair)."""
    labels = list_labels(vault_path)
    seen: Dict[str, int] = {}
    for lbl in labels:
        seen[lbl] = seen.get(lbl, 0) + 1
    return [lbl for lbl, count in seen.items() if count > 1]

"""Diff utilities for comparing .env vault entries across versions."""

from __future__ import annotations

from typing import Any

from envault.vault import _load_vault_raw
from envault.crypto import decrypt


def _decrypt_entry(entry: dict, password: str) -> str:
    """Decrypt a single vault entry and return plaintext value."""
    return decrypt(entry["value"], password)


def diff_versions(
    vault_path: str,
    label: str,
    password: str,
    version_a: int,
    version_b: int,
) -> dict[str, Any]:
    """Return a diff dict comparing two versions of a labelled entry.

    Returns a dict with keys:
        label, version_a, version_b, changed (bool),
        value_a (str | None), value_b (str | None)
    """
    vault = _load_vault_raw(vault_path)
    entries = [
        e for e in vault.get("entries", []) if e.get("label") == label
    ]

    def _find(ver: int) -> dict | None:
        return next((e for e in entries if e.get("version") == ver), None)

    entry_a = _find(version_a)
    entry_b = _find(version_b)

    value_a = _decrypt_entry(entry_a, password) if entry_a else None
    value_b = _decrypt_entry(entry_b, password) if entry_b else None

    return {
        "label": label,
        "version_a": version_a,
        "version_b": version_b,
        "changed": value_a != value_b,
        "value_a": value_a,
        "value_b": value_b,
    }


def diff_labels(
    vault_path: str,
    password: str,
) -> dict[str, list[int]]:
    """Return a mapping of label -> sorted list of available versions."""
    vault = _load_vault_raw(vault_path)
    result: dict[str, list[int]] = {}
    for entry in vault.get("entries", []):
        label = entry.get("label", "")
        version = entry.get("version", 1)
        result.setdefault(label, []).append(version)
    for label in result:
        result[label] = sorted(set(result[label]))
    return result

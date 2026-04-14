"""Merge two vaults or env snapshots, resolving conflicts by strategy."""
from __future__ import annotations

from typing import Literal, NamedTuple

from envault.vault import _load_vault_raw, add_entry, get_entry, list_entries

MergeStrategy = Literal["ours", "theirs", "newest", "error"]


class MergeConflict(NamedTuple):
    label: str
    ours_version: int
    theirs_version: int


class MergeResult(NamedTuple):
    added: list[str]
    updated: list[str]
    skipped: list[str]
    conflicts: list[MergeConflict]


def merge_vaults(
    base_vault_path: str,
    other_vault_path: str,
    password: str,
    strategy: MergeStrategy = "newest",
) -> MergeResult:
    """Merge entries from *other* vault into *base* vault.

    Parameters
    ----------
    base_vault_path:  path to the vault that will be mutated.
    other_vault_path: path to the source vault (read-only).
    password:         shared encryption password (must work for both vaults).
    strategy:         conflict resolution — 'ours' keeps base, 'theirs' keeps
                      other, 'newest' picks the higher version index, 'error'
                      raises on any conflict.
    """
    added: list[str] = []
    updated: list[str] = []
    skipped: list[str] = []
    conflicts: list[MergeConflict] = []

    other_raw = _load_vault_raw(other_vault_path)
    other_entries = other_raw.get("entries", {})

    base_labels = {e["label"] for e in list_entries(base_vault_path)}

    for label, other_entry in other_entries.items():
        other_version = other_entry.get("version", 1)

        if label not in base_labels:
            # New label — import directly.
            value = get_entry(other_vault_path, label, password)
            add_entry(base_vault_path, label, value, password)
            added.append(label)
            continue

        base_raw = _load_vault_raw(base_vault_path)
        base_entry = base_raw["entries"].get(label, {})
        base_version = base_entry.get("version", 1)

        if other_version == base_version:
            skipped.append(label)
            continue

        conflict = MergeConflict(label, base_version, other_version)

        if strategy == "error":
            conflicts.append(conflict)
            continue

        take_other = (
            strategy == "theirs"
            or (strategy == "newest" and other_version > base_version)
        )

        if take_other:
            value = get_entry(other_vault_path, label, password)
            add_entry(base_vault_path, label, value, password)
            updated.append(label)
        else:
            skipped.append(label)

    return MergeResult(
        added=added,
        updated=updated,
        skipped=skipped,
        conflicts=conflicts,
    )

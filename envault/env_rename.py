"""Rename labels across the vault, updating tags, notes, aliases, and expiry metadata."""

from __future__ import annotations

from typing import Optional

from envault.vault import _load_vault_raw, _save_vault_raw


class RenameError(Exception):
    """Raised when a rename operation cannot be completed."""


def rename_label(
    vault_dir: str,
    old_label: str,
    new_label: str,
    *,
    overwrite: bool = False,
) -> None:
    """Rename *old_label* to *new_label* inside the vault.

    Raises
    ------
    RenameError
        If *old_label* does not exist, *new_label* already exists and
        *overwrite* is False, or either label is empty.
    """
    if not old_label or not old_label.strip():
        raise RenameError("old_label must not be empty")
    if not new_label or not new_label.strip():
        raise RenameError("new_label must not be empty")
    if old_label == new_label:
        raise RenameError("old_label and new_label are identical")

    vault = _load_vault_raw(vault_dir)
    entries = vault.get("entries", [])

    old_idx = next((i for i, e in enumerate(entries) if e["label"] == old_label), None)
    if old_idx is None:
        raise RenameError(f"Label '{old_label}' not found in vault")

    new_exists = any(e["label"] == new_label for e in entries)
    if new_exists and not overwrite:
        raise RenameError(
            f"Label '{new_label}' already exists. Pass overwrite=True to replace it."
        )

    if new_exists and overwrite:
        entries = [e for e in entries if e["label"] != new_label]
        old_idx = next(i for i, e in enumerate(entries) if e["label"] == old_label)

    entries[old_idx] = dict(entries[old_idx], label=new_label)
    vault["entries"] = entries
    _save_vault_raw(vault_dir, vault)

    _patch_sidecar_files(vault_dir, old_label, new_label)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _patch_sidecar_files(vault_dir: str, old_label: str, new_label: str) -> None:
    """Best-effort rename of metadata stored in sidecar JSON files."""
    _patch_tags(vault_dir, old_label, new_label)
    _patch_notes(vault_dir, old_label, new_label)
    _patch_aliases(vault_dir, old_label, new_label)
    _patch_expiry(vault_dir, old_label, new_label)


def _patch_tags(vault_dir: str, old_label: str, new_label: str) -> None:
    try:
        from envault.tags import _load_tags, _save_tags
        data = _load_tags(vault_dir)
        if old_label in data:
            data[new_label] = data.pop(old_label)
            _save_tags(vault_dir, data)
    except Exception:
        pass


def _patch_notes(vault_dir: str, old_label: str, new_label: str) -> None:
    try:
        from envault.notes import _load_notes, _save_notes
        data = _load_notes(vault_dir)
        if old_label in data:
            data[new_label] = data.pop(old_label)
            _save_notes(vault_dir, data)
    except Exception:
        pass


def _patch_aliases(vault_dir: str, old_label: str, new_label: str) -> None:
    try:
        from envault.aliases import _load_aliases, _save_aliases
        data = _load_aliases(vault_dir)
        if old_label in data:
            data[new_label] = data.pop(old_label)
            _save_aliases(vault_dir, data)
    except Exception:
        pass


def _patch_expiry(vault_dir: str, old_label: str, new_label: str) -> None:
    try:
        from envault.expiry import _load_expiry, _save_expiry
        data = _load_expiry(vault_dir)
        if old_label in data:
            data[new_label] = data.pop(old_label)
            _save_expiry(vault_dir, data)
    except Exception:
        pass

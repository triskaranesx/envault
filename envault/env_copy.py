"""Copy or rename entries within a vault."""

from __future__ import annotations

from typing import Optional

from envault.vault import _load_vault_raw, _save_vault_raw, get_entry, add_entry


class CopyError(Exception):
    """Raised when a copy or rename operation fails."""


def copy_entry(
    vault_path: str,
    src_label: str,
    dst_label: str,
    password: str,
    overwrite: bool = False,
) -> dict:
    """Copy *src_label* to *dst_label* inside the vault.

    Returns the newly created entry dict.
    Raises CopyError if the source does not exist or destination already
    exists and *overwrite* is False.
    """
    vault = _load_vault_raw(vault_path)
    entries = vault.get("entries", [])

    src_entry = next((e for e in entries if e["label"] == src_label), None)
    if src_entry is None:
        raise CopyError(f"Source label '{src_label}' not found.")

    dst_exists = any(e["label"] == dst_label for e in entries)
    if dst_exists and not overwrite:
        raise CopyError(
            f"Destination label '{dst_label}' already exists. Use overwrite=True to replace it."
        )

    # Decrypt the source value so we can re-encrypt under the same password
    # via add_entry, which handles versioning correctly.
    from envault.crypto import decrypt

    plaintext = decrypt(src_entry["value"], password)

    if dst_exists and overwrite:
        # Remove the existing destination entry first.
        vault["entries"] = [e for e in vault["entries"] if e["label"] != dst_label]
        _save_vault_raw(vault_path, vault)

    new_entry = add_entry(vault_path, dst_label, plaintext, password)
    return new_entry


def rename_entry(
    vault_path: str,
    src_label: str,
    dst_label: str,
    password: str,
    overwrite: bool = False,
) -> dict:
    """Rename *src_label* to *dst_label*.

    Equivalent to copy + delete of the source entry.
    Returns the newly created entry dict.
    """
    new_entry = copy_entry(vault_path, src_label, dst_label, password, overwrite)

    vault = _load_vault_raw(vault_path)
    vault["entries"] = [e for e in vault["entries"] if e["label"] != src_label]
    _save_vault_raw(vault_path, vault)

    return new_entry

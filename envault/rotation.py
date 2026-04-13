"""Key rotation support for envault vaults."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from envault.crypto import decrypt, encrypt
from envault.vault import _load_vault_raw, _save_vault_raw
from envault.history import record_change


def rotate_password(
    vault_path: Path,
    old_password: str,
    new_password: str,
) -> int:
    """Re-encrypt every entry in the vault with *new_password*.

    Returns the number of entries that were rotated.
    Raises ``ValueError`` if *old_password* is wrong (propagated from decrypt).
    """
    vault = _load_vault_raw(vault_path)
    entries: list[dict[str, Any]] = vault.get("entries", [])
    rotated = 0

    for entry in entries:
        token: str = entry["token"]
        # Decrypt with old password — will raise ValueError on wrong password
        plaintext = decrypt(token, old_password)
        # Re-encrypt with new password
        entry["token"] = encrypt(plaintext, new_password)
        rotated += 1

    _save_vault_raw(vault_path, vault)

    if rotated:
        record_change(
            vault_path,
            action="rotate",
            label="*",
            detail=f"rotated {rotated} entries to new password",
        )

    return rotated


def rotate_entry(
    vault_path: Path,
    label: str,
    old_password: str,
    new_password: str,
) -> bool:
    """Re-encrypt a single entry identified by *label*.

    Returns ``True`` if the entry was found and rotated, ``False`` otherwise.
    """
    vault = _load_vault_raw(vault_path)
    entries: list[dict[str, Any]] = vault.get("entries", [])

    for entry in entries:
        if entry.get("label") == label:
            plaintext = decrypt(entry["token"], old_password)
            entry["token"] = encrypt(plaintext, new_password)
            _save_vault_raw(vault_path, vault)
            record_change(
                vault_path,
                action="rotate",
                label=label,
                detail="re-encrypted with new password",
            )
            return True

    return False

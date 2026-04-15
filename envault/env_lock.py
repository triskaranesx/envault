"""envault/env_lock.py

Provides vault locking and unlocking functionality.
A locked vault prevents any read or write operations until unlocked
with the correct password. Lock state is stored in a lightweight
sidecar file alongside vault.json.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

from envault.crypto import encrypt, decrypt

# Name of the lock-state sidecar file inside the vault directory
_LOCK_FILE = ".vault.lock"


def _lock_path(vault_dir: str | Path) -> Path:
    """Return the path to the lock sidecar file."""
    return Path(vault_dir) / _LOCK_FILE


def is_locked(vault_dir: str | Path) -> bool:
    """Return True if the vault currently has an active lock file."""
    return _lock_path(vault_dir).exists()


def lock_vault(vault_dir: str | Path, password: str, actor: str = "unknown") -> None:
    """Lock the vault.

    Writes an encrypted sentinel token to the lock sidecar file.  The
    token embeds the actor name and a Unix timestamp so that audit tools
    can surface who locked the vault and when.

    Args:
        vault_dir: Path to the vault directory (contains vault.json).
        password:  Password used to encrypt the sentinel token.
        actor:     Identifier of the user/process locking the vault.

    Raises:
        FileNotFoundError: If *vault_dir* does not exist.
        RuntimeError:      If the vault is already locked.
    """
    vault_dir = Path(vault_dir)
    if not vault_dir.is_dir():
        raise FileNotFoundError(f"Vault directory not found: {vault_dir}")
    if is_locked(vault_dir):
        raise RuntimeError("Vault is already locked.")

    payload = json.dumps({"actor": actor, "locked_at": time.time()})
    token = encrypt(payload, password)
    _lock_path(vault_dir).write_text(token, encoding="utf-8")


def unlock_vault(vault_dir: str | Path, password: str) -> dict:
    """Unlock the vault.

    Decrypts and removes the lock sidecar file, returning the lock
    metadata (actor and timestamp) so callers can log the event.

    Args:
        vault_dir: Path to the vault directory.
        password:  Password that was used to lock the vault.

    Returns:
        A dict with keys ``actor`` and ``locked_at`` (Unix timestamp).

    Raises:
        RuntimeError:      If the vault is not currently locked.
        ValueError:        If *password* is incorrect or the token is corrupt.
    """
    vault_dir = Path(vault_dir)
    lock_file = _lock_path(vault_dir)

    if not lock_file.exists():
        raise RuntimeError("Vault is not locked.")

    token = lock_file.read_text(encoding="utf-8")
    try:
        payload = decrypt(token, password)
    except Exception as exc:
        raise ValueError("Incorrect password or corrupted lock file.") from exc

    metadata: dict = json.loads(payload)
    lock_file.unlink()
    return metadata


def get_lock_info(vault_dir: str | Path, password: str) -> Optional[dict]:
    """Return lock metadata without removing the lock, or None if unlocked.

    Args:
        vault_dir: Path to the vault directory.
        password:  Password used to lock the vault.

    Returns:
        Dict with ``actor`` and ``locked_at`` keys, or ``None``.

    Raises:
        ValueError: If the password is wrong or the token is corrupted.
    """
    vault_dir = Path(vault_dir)
    lock_file = _lock_path(vault_dir)

    if not lock_file.exists():
        return None

    token = lock_file.read_text(encoding="utf-8")
    try:
        payload = decrypt(token, password)
    except Exception as exc:
        raise ValueError("Incorrect password or corrupted lock file.") from exc

    return json.loads(payload)

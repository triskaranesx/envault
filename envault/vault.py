"""Vault module for reading, writing, and versioning encrypted .env vault files."""

import json
import os
import time
from pathlib import Path
from typing import Optional

from envault.crypto import encrypt, decrypt

DEFAULT_VAULT_FILE = ".envault"
VAULT_VERSION = 1


def _load_vault_raw(vault_path: Path) -> dict:
    """Load and parse the raw JSON vault file."""
    if not vault_path.exists():
        raise FileNotFoundError(f"Vault file not found: {vault_path}")
    with vault_path.open("r") as f:
        return json.load(f)


def _save_vault_raw(vault_path: Path, data: dict) -> None:
    """Persist the vault dict as formatted JSON."""
    with vault_path.open("w") as f:
        json.dump(data, f, indent=2)


def init_vault(vault_path: Path = Path(DEFAULT_VAULT_FILE)) -> dict:
    """Create a new, empty vault structure (does not write to disk)."""
    return {
        "version": VAULT_VERSION,
        "created_at": int(time.time()),
        "entries": [],
    }


def add_entry(
    vault: dict,
    password: str,
    env_content: str,
    label: Optional[str] = None,
) -> dict:
    """Encrypt env_content and append a new versioned entry to the vault."""
    blob = encrypt(password, env_content)
    entry = {
        "index": len(vault["entries"]) + 1,
        "timestamp": int(time.time()),
        "label": label or "",
        "blob": blob,
    }
    vault["entries"].append(entry)
    return entry


def get_entry(vault: dict, password: str, index: int = -1) -> str:
    """Decrypt and return the env content for the given entry index.

    index=-1 returns the latest entry.
    """
    if not vault["entries"]:
        raise ValueError("Vault contains no entries.")
    entry = vault["entries"][index]
    return decrypt(password, entry["blob"])


def list_entries(vault: dict) -> list[dict]:
    """Return a summary list of entries (without blobs)."""
    return [
        {
            "index": e["index"],
            "timestamp": e["timestamp"],
            "label": e["label"],
        }
        for e in vault["entries"]
    ]


def save_vault(vault: dict, vault_path: Path = Path(DEFAULT_VAULT_FILE)) -> None:
    """Write the vault to disk."""
    _save_vault_raw(vault_path, vault)


def load_vault(vault_path: Path = Path(DEFAULT_VAULT_FILE)) -> dict:
    """Load a vault from disk."""
    return _load_vault_raw(vault_path)

"""Backup and restore vault snapshots to/from local archive files."""

import json
import os
import shutil
import time
from pathlib import Path

BACKUP_DIR_NAME = ".envault_backups"


def _backup_dir(vault_path: str) -> Path:
    return Path(vault_path) / BACKUP_DIR_NAME


def create_backup(vault_path: str, label: str | None = None) -> str:
    """Create a timestamped backup of the vault directory.

    Returns the path to the created backup archive.
    """
    vault = Path(vault_path)
    if not vault.exists():
        raise FileNotFoundError(f"Vault not found: {vault_path}")

    backup_dir = _backup_dir(vault_path)
    backup_dir.mkdir(exist_ok=True)

    timestamp = int(time.time())
    slug = f"_{label}" if label else ""
    archive_name = f"backup_{timestamp}{slug}"
    archive_path = backup_dir / archive_name

    # Copy vault contents (excluding the backup dir itself)
    tmp_stage = backup_dir / f"_stage_{timestamp}"
    tmp_stage.mkdir()
    try:
        for item in vault.iterdir():
            if item.name == BACKUP_DIR_NAME:
                continue
            dest = tmp_stage / item.name
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)
        shutil.make_archive(str(archive_path), "zip", root_dir=str(tmp_stage))
    finally:
        shutil.rmtree(tmp_stage, ignore_errors=True)

    return str(archive_path) + ".zip"


def list_backups(vault_path: str) -> list[dict]:
    """Return metadata for all available backups, newest first."""
    backup_dir = _backup_dir(vault_path)
    if not backup_dir.exists():
        return []

    backups = []
    for f in sorted(backup_dir.glob("backup_*.zip"), reverse=True):
        stem = f.stem  # e.g. backup_1700000000_mylabel
        parts = stem.split("_", 2)
        ts = int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else 0
        label = parts[2] if len(parts) == 3 else None
        backups.append({"file": str(f), "timestamp": ts, "label": label})
    return backups


def restore_backup(vault_path: str, backup_file: str) -> None:
    """Restore vault contents from a backup archive.

    Existing vault files (except the backup dir) are removed before restore.
    """
    vault = Path(vault_path)
    archive = Path(backup_file)
    if not archive.exists():
        raise FileNotFoundError(f"Backup file not found: {backup_file}")

    # Remove current vault files (keep backup dir)
    for item in vault.iterdir():
        if item.name == BACKUP_DIR_NAME:
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    shutil.unpack_archive(str(archive), extract_dir=str(vault))

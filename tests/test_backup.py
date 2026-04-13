"""Tests for envault.backup module."""

import os
import time
import zipfile
from pathlib import Path

import pytest

from envault.backup import create_backup, list_backups, restore_backup
from envault.vault import init_vault, add_entry

PASSWORD = "test-pass"


@pytest.fixture()
def vault_dir(tmp_path):
    vp = str(tmp_path / "vault")
    init_vault(vp, PASSWORD)
    add_entry(vp, PASSWORD, "DB_URL", "postgres://localhost/dev")
    add_entry(vp, PASSWORD, "SECRET_KEY", "supersecret")
    return vp


# ---------------------------------------------------------------------------
# create_backup
# ---------------------------------------------------------------------------

def test_create_backup_returns_zip_path(vault_dir):
    path = create_backup(vault_dir)
    assert path.endswith(".zip")
    assert Path(path).exists()


def test_create_backup_archive_contains_vault_json(vault_dir):
    path = create_backup(vault_dir)
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
    assert any("vault.json" in n for n in names)


def test_create_backup_with_label(vault_dir):
    path = create_backup(vault_dir, label="before-deploy")
    assert "before-deploy" in Path(path).name


def test_create_backup_nonexistent_vault(tmp_path):
    with pytest.raises(FileNotFoundError):
        create_backup(str(tmp_path / "no_such_vault"))


# ---------------------------------------------------------------------------
# list_backups
# ---------------------------------------------------------------------------

def test_list_backups_empty_when_none_exist(vault_dir):
    assert list_backups(vault_dir) == []


def test_list_backups_returns_entries(vault_dir):
    create_backup(vault_dir, label="v1")
    create_backup(vault_dir, label="v2")
    backups = list_backups(vault_dir)
    assert len(backups) == 2


def test_list_backups_newest_first(vault_dir):
    create_backup(vault_dir, label="first")
    time.sleep(0.01)
    create_backup(vault_dir, label="second")
    backups = list_backups(vault_dir)
    assert backups[0]["label"] == "second"
    assert backups[1]["label"] == "first"


def test_list_backups_metadata_fields(vault_dir):
    create_backup(vault_dir, label="meta")
    entry = list_backups(vault_dir)[0]
    assert "file" in entry
    assert "timestamp" in entry
    assert entry["label"] == "meta"


# ---------------------------------------------------------------------------
# restore_backup
# ---------------------------------------------------------------------------

def test_restore_backup_recovers_vault(vault_dir):
    backup_path = create_backup(vault_dir)
    # Corrupt the vault by removing vault.json
    (Path(vault_dir) / "vault.json").unlink()
    assert not (Path(vault_dir) / "vault.json").exists()

    restore_backup(vault_dir, backup_path)
    assert (Path(vault_dir) / "vault.json").exists()


def test_restore_backup_missing_file_raises(vault_dir):
    with pytest.raises(FileNotFoundError):
        restore_backup(vault_dir, "/nonexistent/backup.zip")

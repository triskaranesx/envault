"""Unit tests for envault.env_rename."""

from __future__ import annotations

import json
import os
import pytest

from envault.vault import init_vault, add_entry
from envault.env_rename import rename_label, RenameError


PASSWORD = "secret"


@pytest.fixture()
def vault_dir(tmp_path):
    vd = str(tmp_path)
    init_vault(vd, PASSWORD)
    add_entry(vd, PASSWORD, "DB_HOST", "localhost")
    add_entry(vd, PASSWORD, "DB_PORT", "5432")
    return vd


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

def test_rename_changes_label(vault_dir):
    rename_label(vault_dir, "DB_HOST", "DATABASE_HOST")
    vault_file = os.path.join(vault_dir, "vault.json")
    data = json.loads(open(vault_file).read())
    labels = [e["label"] for e in data["entries"]]
    assert "DATABASE_HOST" in labels
    assert "DB_HOST" not in labels


def test_rename_preserves_other_labels(vault_dir):
    rename_label(vault_dir, "DB_HOST", "DATABASE_HOST")
    vault_file = os.path.join(vault_dir, "vault.json")
    data = json.loads(open(vault_file).read())
    labels = [e["label"] for e in data["entries"]]
    assert "DB_PORT" in labels


def test_rename_preserves_encrypted_value(vault_dir):
    """The ciphertext blob must survive the rename unchanged."""
    vault_file = os.path.join(vault_dir, "vault.json")
    before = json.loads(open(vault_file).read())
    old_blob = next(e["value"] for e in before["entries"] if e["label"] == "DB_HOST")

    rename_label(vault_dir, "DB_HOST", "DATABASE_HOST")

    after = json.loads(open(vault_file).read())
    new_blob = next(e["value"] for e in after["entries"] if e["label"] == "DATABASE_HOST")
    assert old_blob == new_blob


def test_rename_with_overwrite_replaces_existing(vault_dir):
    rename_label(vault_dir, "DB_HOST", "DB_PORT", overwrite=True)
    vault_file = os.path.join(vault_dir, "vault.json")
    data = json.loads(open(vault_file).read())
    labels = [e["label"] for e in data["entries"]]
    assert labels.count("DB_PORT") == 1
    assert "DB_HOST" not in labels


# ---------------------------------------------------------------------------
# Error-path tests
# ---------------------------------------------------------------------------

def test_rename_missing_old_label_raises(vault_dir):
    with pytest.raises(RenameError, match="not found"):
        rename_label(vault_dir, "NONEXISTENT", "NEW_LABEL")


def test_rename_existing_new_label_raises_without_overwrite(vault_dir):
    with pytest.raises(RenameError, match="already exists"):
        rename_label(vault_dir, "DB_HOST", "DB_PORT")


def test_rename_empty_old_label_raises(vault_dir):
    with pytest.raises(RenameError, match="old_label"):
        rename_label(vault_dir, "", "NEW")


def test_rename_empty_new_label_raises(vault_dir):
    with pytest.raises(RenameError, match="new_label"):
        rename_label(vault_dir, "DB_HOST", "")


def test_rename_identical_labels_raises(vault_dir):
    with pytest.raises(RenameError, match="identical"):
        rename_label(vault_dir, "DB_HOST", "DB_HOST")

"""Tests for envault.env_copy (copy / rename entries)."""

from __future__ import annotations

import pytest

from envault.vault import init_vault, add_entry, get_entry, _load_vault_raw
from envault.env_copy import copy_entry, rename_entry, CopyError


PASSWORD = "test-secret"


@pytest.fixture()
def vault_dir(tmp_path):
    vp = str(tmp_path / "vault.json")
    init_vault(vp)
    add_entry(vp, "DB_HOST", "localhost", PASSWORD)
    add_entry(vp, "DB_PORT", "5432", PASSWORD)
    return vp


# ---------------------------------------------------------------------------
# copy_entry
# ---------------------------------------------------------------------------

def test_copy_entry_creates_destination(vault_dir):
    new_entry = copy_entry(vault_dir, "DB_HOST", "DB_HOST_COPY", PASSWORD)
    assert new_entry["label"] == "DB_HOST_COPY"


def test_copy_entry_value_matches_source(vault_dir):
    copy_entry(vault_dir, "DB_HOST", "DB_HOST_COPY", PASSWORD)
    value = get_entry(vault_dir, "DB_HOST_COPY", PASSWORD)
    assert value == "localhost"


def test_copy_entry_source_still_exists(vault_dir):
    copy_entry(vault_dir, "DB_HOST", "DB_HOST_COPY", PASSWORD)
    value = get_entry(vault_dir, "DB_HOST", PASSWORD)
    assert value == "localhost"


def test_copy_entry_missing_source_raises(vault_dir):
    with pytest.raises(CopyError, match="Source label"):
        copy_entry(vault_dir, "NONEXISTENT", "NEW_LABEL", PASSWORD)


def test_copy_entry_existing_destination_raises_without_overwrite(vault_dir):
    with pytest.raises(CopyError, match="already exists"):
        copy_entry(vault_dir, "DB_HOST", "DB_PORT", PASSWORD)


def test_copy_entry_overwrite_replaces_destination(vault_dir):
    copy_entry(vault_dir, "DB_HOST", "DB_PORT", PASSWORD, overwrite=True)
    value = get_entry(vault_dir, "DB_PORT", PASSWORD)
    assert value == "localhost"


def test_copy_entry_overwrite_keeps_single_destination(vault_dir):
    copy_entry(vault_dir, "DB_HOST", "DB_PORT", PASSWORD, overwrite=True)
    vault = _load_vault_raw(vault_dir)
    labels = [e["label"] for e in vault["entries"]]
    assert labels.count("DB_PORT") == 1


# ---------------------------------------------------------------------------
# rename_entry
# ---------------------------------------------------------------------------

def test_rename_entry_creates_destination(vault_dir):
    rename_entry(vault_dir, "DB_HOST", "DB_HOSTNAME", PASSWORD)
    value = get_entry(vault_dir, "DB_HOSTNAME", PASSWORD)
    assert value == "localhost"


def test_rename_entry_removes_source(vault_dir):
    rename_entry(vault_dir, "DB_HOST", "DB_HOSTNAME", PASSWORD)
    vault = _load_vault_raw(vault_dir)
    labels = [e["label"] for e in vault["entries"]]
    assert "DB_HOST" not in labels


def test_rename_entry_missing_source_raises(vault_dir):
    with pytest.raises(CopyError, match="Source label"):
        rename_entry(vault_dir, "GHOST", "NEW", PASSWORD)


def test_rename_entry_existing_destination_raises_without_overwrite(vault_dir):
    with pytest.raises(CopyError, match="already exists"):
        rename_entry(vault_dir, "DB_HOST", "DB_PORT", PASSWORD)

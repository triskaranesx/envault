"""Tests for envault.vault — versioned encrypted vault operations."""

import json
import time
from pathlib import Path

import pytest

from envault.vault import (
    add_entry,
    get_entry,
    init_vault,
    list_entries,
    load_vault,
    save_vault,
)

PASSWORD = "s3cr3t!"
ENV_CONTENT = "API_KEY=abc123\nDB_URL=postgres://localhost/dev\n"


@pytest.fixture()
def empty_vault():
    return init_vault()


@pytest.fixture()
def vault_with_entry(empty_vault):
    add_entry(empty_vault, PASSWORD, ENV_CONTENT, label="v1")
    return empty_vault


def test_init_vault_structure(empty_vault):
    assert "version" in empty_vault
    assert "entries" in empty_vault
    assert empty_vault["entries"] == []


def test_add_entry_increments_index(empty_vault):
    e1 = add_entry(empty_vault, PASSWORD, ENV_CONTENT)
    e2 = add_entry(empty_vault, PASSWORD, "OTHER=1\n")
    assert e1["index"] == 1
    assert e2["index"] == 2
    assert len(empty_vault["entries"]) == 2


def test_add_entry_stores_label(empty_vault):
    entry = add_entry(empty_vault, PASSWORD, ENV_CONTENT, label="production")
    assert entry["label"] == "production"


def test_get_entry_latest_roundtrip(vault_with_entry):
    result = get_entry(vault_with_entry, PASSWORD)
    assert result == ENV_CONTENT


def test_get_entry_by_index(empty_vault):
    add_entry(empty_vault, PASSWORD, "FIRST=1\n", label="first")
    add_entry(empty_vault, PASSWORD, "SECOND=2\n", label="second")
    assert get_entry(empty_vault, PASSWORD, index=0) == "FIRST=1\n"
    assert get_entry(empty_vault, PASSWORD, index=1) == "SECOND=2\n"


def test_get_entry_wrong_password_raises(vault_with_entry):
    with pytest.raises(Exception):
        get_entry(vault_with_entry, "wrongpassword")


def test_get_entry_empty_vault_raises(empty_vault):
    with pytest.raises(ValueError, match="no entries"):
        get_entry(empty_vault, PASSWORD)


def test_list_entries_no_blobs(vault_with_entry):
    add_entry(vault_with_entry, PASSWORD, "X=1\n", label="v2")
    summaries = list_entries(vault_with_entry)
    assert len(summaries) == 2
    for s in summaries:
        assert "blob" not in s
        assert "index" in s
        assert "timestamp" in s
        assert "label" in s


def test_save_and_load_vault_roundtrip(tmp_path, vault_with_entry):
    vault_file = tmp_path / ".envault"
    save_vault(vault_with_entry, vault_path=vault_file)
    assert vault_file.exists()
    loaded = load_vault(vault_path=vault_file)
    assert get_entry(loaded, PASSWORD) == ENV_CONTENT


def test_load_vault_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_vault(vault_path=tmp_path / "nonexistent.envault")

import pytest
import os
from envault.vault import init_vault, add_entry
from envault.env_labels import (
    list_labels,
    normalize_labels,
    bulk_rename_labels,
    find_duplicate_labels,
    LabelError,
)

PASSWORD = "testpass"


@pytest.fixture
def vault_dir(tmp_path):
    vp = str(tmp_path / "vault.json")
    init_vault(vp)
    add_entry(vp, "db_host", "localhost", PASSWORD)
    add_entry(vp, "api_key", "secret", PASSWORD)
    add_entry(vp, "debug", "true", PASSWORD)
    return vp


def test_list_labels_returns_all(vault_dir):
    labels = list_labels(vault_dir)
    assert set(labels) == {"db_host", "api_key", "debug"}


def test_list_labels_empty_vault(tmp_path):
    vp = str(tmp_path / "vault.json")
    init_vault(vp)
    assert list_labels(vp) == []


def test_normalize_labels_uppercases(vault_dir):
    mapping = normalize_labels(vault_dir)
    assert "db_host" in mapping
    assert mapping["db_host"] == "DB_HOST"
    labels = list_labels(vault_dir)
    assert "DB_HOST" in labels
    assert "db_host" not in labels


def test_normalize_labels_returns_empty_when_already_upper(tmp_path):
    vp = str(tmp_path / "vault.json")
    init_vault(vp)
    add_entry(vp, "ALREADY", "val", PASSWORD)
    mapping = normalize_labels(vp)
    assert mapping == {}


def test_bulk_rename_labels_success(vault_dir):
    changed = bulk_rename_labels(vault_dir, {"db_host": "database_host"})
    assert "database_host" in changed
    labels = list_labels(vault_dir)
    assert "database_host" in labels
    assert "db_host" not in labels


def test_bulk_rename_labels_missing_source_raises(vault_dir):
    with pytest.raises(LabelError, match="not found"):
        bulk_rename_labels(vault_dir, {"nonexistent": "something"})


def test_bulk_rename_labels_empty_mapping_raises(vault_dir):
    with pytest.raises(LabelError, match="empty"):
        bulk_rename_labels(vault_dir, {})


def test_bulk_rename_labels_target_exists_raises(vault_dir):
    with pytest.raises(LabelError, match="already exists"):
        bulk_rename_labels(vault_dir, {"db_host": "api_key"})


def test_find_duplicate_labels_none(vault_dir):
    assert find_duplicate_labels(vault_dir) == []

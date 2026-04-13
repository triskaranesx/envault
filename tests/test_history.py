"""Tests for envault.history module."""

import pytest
from envault.history import record_change, get_history, clear_history


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path)


def test_empty_history_returns_list(tmp_vault):
    result = get_history(vault_dir=tmp_vault)
    assert result == []


def test_record_change_creates_entry(tmp_vault):
    record_change("DB_URL", 1, "add", vault_dir=tmp_vault)
    history = get_history(vault_dir=tmp_vault)
    assert len(history) == 1
    entry = history[0]
    assert entry["label"] == "DB_URL"
    assert entry["version"] == 1
    assert entry["action"] == "add"


def test_record_change_includes_timestamp(tmp_vault):
    record_change("SECRET", 1, "add", vault_dir=tmp_vault)
    history = get_history(vault_dir=tmp_vault)
    assert "timestamp" in history[0]
    assert history[0]["timestamp"].endswith("Z")


def test_record_multiple_changes(tmp_vault):
    record_change("KEY_A", 1, "add", vault_dir=tmp_vault)
    record_change("KEY_A", 2, "update", vault_dir=tmp_vault)
    record_change("KEY_B", 1, "add", vault_dir=tmp_vault)
    history = get_history(vault_dir=tmp_vault)
    assert len(history) == 3


def test_get_history_filter_by_label(tmp_vault):
    record_change("KEY_A", 1, "add", vault_dir=tmp_vault)
    record_change("KEY_B", 1, "add", vault_dir=tmp_vault)
    record_change("KEY_A", 2, "update", vault_dir=tmp_vault)
    filtered = get_history(label="KEY_A", vault_dir=tmp_vault)
    assert len(filtered) == 2
    assert all(e["label"] == "KEY_A" for e in filtered)


def test_clear_history(tmp_vault):
    record_change("KEY_A", 1, "add", vault_dir=tmp_vault)
    clear_history(vault_dir=tmp_vault)
    assert get_history(vault_dir=tmp_vault) == []


def test_actor_default_is_local(tmp_vault):
    record_change("KEY", 1, "add", vault_dir=tmp_vault)
    entry = get_history(vault_dir=tmp_vault)[0]
    assert entry["actor"] == "local"


def test_custom_actor(tmp_vault):
    record_change("KEY", 1, "add", actor="alice", vault_dir=tmp_vault)
    entry = get_history(vault_dir=tmp_vault)[0]
    assert entry["actor"] == "alice"

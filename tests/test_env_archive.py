import json
import pytest
from pathlib import Path
from envault import env_archive as arc


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


SAMPLE = {"label": "DB_PASS", "ciphertext": "abc123", "version": 1}


def test_list_archived_empty(vault_dir):
    assert arc.list_archived(vault_dir) == []


def test_archive_entry_creates_entry(vault_dir):
    arc.archive_entry(vault_dir, "DB_PASS", SAMPLE)
    assert "DB_PASS" in arc.list_archived(vault_dir)


def test_get_archived_returns_entry(vault_dir):
    arc.archive_entry(vault_dir, "DB_PASS", SAMPLE)
    result = arc.get_archived(vault_dir, "DB_PASS")
    assert result == SAMPLE


def test_get_archived_returns_none_when_absent(vault_dir):
    assert arc.get_archived(vault_dir, "MISSING") is None


def test_archive_persists_as_json(vault_dir):
    arc.archive_entry(vault_dir, "KEY", SAMPLE)
    raw = json.loads((Path(vault_dir) / ".archive.json").read_text())
    assert "KEY" in raw


def test_restore_entry_removes_from_archive(vault_dir):
    arc.archive_entry(vault_dir, "DB_PASS", SAMPLE)
    arc.restore_entry(vault_dir, "DB_PASS")
    assert arc.get_archived(vault_dir, "DB_PASS") is None


def test_restore_entry_returns_original(vault_dir):
    arc.archive_entry(vault_dir, "DB_PASS", SAMPLE)
    entry = arc.restore_entry(vault_dir, "DB_PASS")
    assert entry == SAMPLE


def test_restore_missing_raises(vault_dir):
    with pytest.raises(KeyError):
        arc.restore_entry(vault_dir, "NOPE")


def test_purge_returns_true_when_exists(vault_dir):
    arc.archive_entry(vault_dir, "X", SAMPLE)
    assert arc.purge_archived(vault_dir, "X") is True
    assert arc.get_archived(vault_dir, "X") is None


def test_purge_returns_false_when_absent(vault_dir):
    assert arc.purge_archived(vault_dir, "GHOST") is False


def test_archive_empty_label_raises(vault_dir):
    with pytest.raises(ValueError):
        arc.archive_entry(vault_dir, "", SAMPLE)


def test_multiple_entries_stored_independently(vault_dir):
    e1 = {"label": "A", "data": "1"}
    e2 = {"label": "B", "data": "2"}
    arc.archive_entry(vault_dir, "A", e1)
    arc.archive_entry(vault_dir, "B", e2)
    assert arc.get_archived(vault_dir, "A") == e1
    assert arc.get_archived(vault_dir, "B") == e2

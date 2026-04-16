import json
from pathlib import Path
import pytest
from envault.env_bookmarks import add_bookmark, remove_bookmark, list_bookmarks


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_bookmarks_file_created_on_first_add(vault_dir):
    add_bookmark(vault_dir, "A")
    assert (Path(vault_dir) / ".bookmarks.json").exists()


def test_bookmarks_persisted_as_json(vault_dir):
    add_bookmark(vault_dir, "DB", note="database")
    raw = json.loads((Path(vault_dir) / ".bookmarks.json").read_text())
    assert "DB" in raw
    assert raw["DB"]["note"] == "database"


def test_multiple_bookmarks_stored_independently(vault_dir):
    add_bookmark(vault_dir, "A", note="first")
    add_bookmark(vault_dir, "B", note="second")
    raw = json.loads((Path(vault_dir) / ".bookmarks.json").read_text())
    assert "A" in raw and "B" in raw


def test_remove_does_not_affect_other_bookmarks(vault_dir):
    add_bookmark(vault_dir, "A")
    add_bookmark(vault_dir, "B")
    remove_bookmark(vault_dir, "A")
    bms = list_bookmarks(vault_dir)
    assert "A" not in bms
    assert "B" in bms


def test_no_file_no_error_on_list(vault_dir):
    result = list_bookmarks(vault_dir)
    assert result == {}

import pytest
from pathlib import Path
from envault.env_bookmarks import (
    add_bookmark, remove_bookmark, get_bookmark,
    list_bookmarks, is_bookmarked,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_list_bookmarks_empty(vault_dir):
    assert list_bookmarks(vault_dir) == {}


def test_add_bookmark_creates_entry(vault_dir):
    add_bookmark(vault_dir, "DB_URL")
    bms = list_bookmarks(vault_dir)
    assert "DB_URL" in bms


def test_add_bookmark_with_note(vault_dir):
    add_bookmark(vault_dir, "API_KEY", note="important key")
    bm = get_bookmark(vault_dir, "API_KEY")
    assert bm["note"] == "important key"


def test_add_bookmark_no_duplicates(vault_dir):
    add_bookmark(vault_dir, "X")
    add_bookmark(vault_dir, "X", note="updated")
    bms = list_bookmarks(vault_dir)
    assert len(bms) == 1
    assert bms["X"]["note"] == "updated"


def test_add_bookmark_empty_label_raises(vault_dir):
    with pytest.raises(ValueError):
        add_bookmark(vault_dir, "")


def test_get_bookmark_returns_none_when_absent(vault_dir):
    assert get_bookmark(vault_dir, "MISSING") is None


def test_remove_bookmark_returns_true(vault_dir):
    add_bookmark(vault_dir, "Z")
    assert remove_bookmark(vault_dir, "Z") is True
    assert get_bookmark(vault_dir, "Z") is None


def test_remove_bookmark_missing_returns_false(vault_dir):
    assert remove_bookmark(vault_dir, "NOPE") is False


def test_is_bookmarked_true(vault_dir):
    add_bookmark(vault_dir, "FOO")
    assert is_bookmarked(vault_dir, "FOO") is True


def test_is_bookmarked_false(vault_dir):
    assert is_bookmarked(vault_dir, "BAR") is False


def test_multiple_bookmarks_stored_independently(vault_dir):
    add_bookmark(vault_dir, "A", note="first")
    add_bookmark(vault_dir, "B", note="second")
    assert get_bookmark(vault_dir, "A")["note"] == "first"
    assert get_bookmark(vault_dir, "B")["note"] == "second"

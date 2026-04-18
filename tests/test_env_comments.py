import pytest
from pathlib import Path
from envault.env_comments import set_comment, get_comment, remove_comment, list_comments


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_get_comment_returns_none_when_absent(vault_dir):
    assert get_comment(vault_dir, "MY_KEY") is None


def test_set_and_get_comment(vault_dir):
    set_comment(vault_dir, "MY_KEY", "This is a secret key")
    assert get_comment(vault_dir, "MY_KEY") == "This is a secret key"


def test_set_comment_strips_whitespace(vault_dir):
    set_comment(vault_dir, "MY_KEY", "  trimmed  ")
    assert get_comment(vault_dir, "MY_KEY") == "trimmed"


def test_set_comment_overwrites_existing(vault_dir):
    set_comment(vault_dir, "MY_KEY", "first")
    set_comment(vault_dir, "MY_KEY", "second")
    assert get_comment(vault_dir, "MY_KEY") == "second"


def test_set_comment_empty_label_raises(vault_dir):
    with pytest.raises(ValueError):
        set_comment(vault_dir, "", "some comment")


def test_set_comment_empty_comment_raises(vault_dir):
    with pytest.raises(ValueError):
        set_comment(vault_dir, "MY_KEY", "")


def test_remove_comment_returns_true(vault_dir):
    set_comment(vault_dir, "MY_KEY", "hello")
    assert remove_comment(vault_dir, "MY_KEY") is True
    assert get_comment(vault_dir, "MY_KEY") is None


def test_remove_comment_missing_returns_false(vault_dir):
    assert remove_comment(vault_dir, "MISSING") is False


def test_list_comments_empty(vault_dir):
    assert list_comments(vault_dir) == {}


def test_list_comments_returns_all(vault_dir):
    set_comment(vault_dir, "A", "comment a")
    set_comment(vault_dir, "B", "comment b")
    data = list_comments(vault_dir)
    assert data == {"A": "comment a", "B": "comment b"}


def test_comments_persisted_as_json(vault_dir):
    set_comment(vault_dir, "X", "persisted")
    p = Path(vault_dir) / ".envault_comments.json"
    assert p.exists()
    import json
    raw = json.loads(p.read_text())
    assert raw["X"] == "persisted"

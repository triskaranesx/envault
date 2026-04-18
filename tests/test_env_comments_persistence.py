import json
from pathlib import Path
import pytest
from envault.env_comments import set_comment, get_comment, remove_comment


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_comments_file_created_on_first_set(vault_dir):
    p = Path(vault_dir) / ".envault_comments.json"
    assert not p.exists()
    set_comment(vault_dir, "K", "v")
    assert p.exists()


def test_multiple_comments_stored_independently(vault_dir):
    set_comment(vault_dir, "A", "alpha")
    set_comment(vault_dir, "B", "beta")
    assert get_comment(vault_dir, "A") == "alpha"
    assert get_comment(vault_dir, "B") == "beta"


def test_remove_does_not_affect_others(vault_dir):
    set_comment(vault_dir, "A", "alpha")
    set_comment(vault_dir, "B", "beta")
    remove_comment(vault_dir, "A")
    assert get_comment(vault_dir, "B") == "beta"


def test_json_structure_is_flat_dict(vault_dir):
    set_comment(vault_dir, "X", "xray")
    set_comment(vault_dir, "Y", "yankee")
    raw = json.loads((Path(vault_dir) / ".envault_comments.json").read_text())
    assert isinstance(raw, dict)
    assert raw["X"] == "xray"
    assert raw["Y"] == "yankee"

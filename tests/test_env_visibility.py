"""Tests for envault.env_visibility."""
import pytest
from pathlib import Path
from envault.env_visibility import (
    set_visibility,
    get_visibility,
    remove_visibility,
    list_visibility,
    filter_by_level,
    VisibilityError,
)


@pytest.fixture()
def vault_dir(tmp_path: Path) -> str:
    return str(tmp_path)


def test_get_visibility_returns_none_when_absent(vault_dir):
    assert get_visibility(vault_dir, "API_KEY") is None


def test_set_and_get_visibility(vault_dir):
    set_visibility(vault_dir, "API_KEY", "private")
    assert get_visibility(vault_dir, "API_KEY") == "private"


def test_set_visibility_overwrites_existing(vault_dir):
    set_visibility(vault_dir, "API_KEY", "public")
    set_visibility(vault_dir, "API_KEY", "masked")
    assert get_visibility(vault_dir, "API_KEY") == "masked"


def test_set_visibility_invalid_level_raises(vault_dir):
    with pytest.raises(VisibilityError, match="invalid level"):
        set_visibility(vault_dir, "API_KEY", "hidden")


def test_set_visibility_empty_label_raises(vault_dir):
    with pytest.raises(VisibilityError, match="label must not be empty"):
        set_visibility(vault_dir, "", "public")


def test_remove_visibility_returns_true_when_exists(vault_dir):
    set_visibility(vault_dir, "TOKEN", "private")
    assert remove_visibility(vault_dir, "TOKEN") is True
    assert get_visibility(vault_dir, "TOKEN") is None


def test_remove_visibility_returns_false_when_absent(vault_dir):
    assert remove_visibility(vault_dir, "GHOST") is False


def test_list_visibility_empty(vault_dir):
    assert list_visibility(vault_dir) == []


def test_list_visibility_returns_all(vault_dir):
    set_visibility(vault_dir, "DB_PASS", "private")
    set_visibility(vault_dir, "APP_ENV", "public")
    result = list_visibility(vault_dir)
    labels = [r["label"] for r in result]
    assert "DB_PASS" in labels
    assert "APP_ENV" in labels
    assert len(result) == 2


def test_list_visibility_sorted_by_label(vault_dir):
    set_visibility(vault_dir, "Z_VAR", "public")
    set_visibility(vault_dir, "A_VAR", "masked")
    labels = [r["label"] for r in list_visibility(vault_dir)]
    assert labels == sorted(labels)


def test_filter_by_level_returns_matching(vault_dir):
    set_visibility(vault_dir, "SECRET", "private")
    set_visibility(vault_dir, "OPEN", "public")
    set_visibility(vault_dir, "HIDDEN", "private")
    result = filter_by_level(vault_dir, "private")
    assert "SECRET" in result
    assert "HIDDEN" in result
    assert "OPEN" not in result


def test_filter_by_level_invalid_level_raises(vault_dir):
    with pytest.raises(VisibilityError, match="invalid level"):
        filter_by_level(vault_dir, "top-secret")


def test_visibility_file_created_on_first_set(vault_dir):
    from pathlib import Path
    vis_file = Path(vault_dir) / ".visibility.json"
    assert not vis_file.exists()
    set_visibility(vault_dir, "KEY", "masked")
    assert vis_file.exists()

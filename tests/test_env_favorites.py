import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.env_favorites import add_favorite, remove_favorite, list_favorites, is_favorite
from envault.cli_favorites import cmd_favorites


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def runner():
    return CliRunner()


def test_list_favorites_empty(vault_dir):
    assert list_favorites(vault_dir) == []


def test_add_favorite_creates_entry(vault_dir):
    add_favorite(vault_dir, "DB_PASSWORD")
    assert "DB_PASSWORD" in list_favorites(vault_dir)


def test_add_favorite_no_duplicates(vault_dir):
    add_favorite(vault_dir, "API_KEY")
    add_favorite(vault_dir, "API_KEY")
    assert list_favorites(vault_dir).count("API_KEY") == 1


def test_add_favorite_empty_label_raises(vault_dir):
    with pytest.raises(ValueError):
        add_favorite(vault_dir, "")


def test_remove_favorite_returns_true(vault_dir):
    add_favorite(vault_dir, "SECRET")
    assert remove_favorite(vault_dir, "SECRET") is True
    assert "SECRET" not in list_favorites(vault_dir)


def test_remove_favorite_missing_returns_false(vault_dir):
    assert remove_favorite(vault_dir, "NONEXISTENT") is False


def test_is_favorite_true(vault_dir):
    add_favorite(vault_dir, "TOKEN")
    assert is_favorite(vault_dir, "TOKEN") is True


def test_is_favorite_false(vault_dir):
    assert is_favorite(vault_dir, "TOKEN") is False


def test_cli_fav_add(runner, vault_dir):
    result = runner.invoke(cmd_favorites, ["add", "DB_URL", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "DB_URL" in result.output


def test_cli_fav_list(runner, vault_dir):
    add_favorite(vault_dir, "MY_KEY")
    result = runner.invoke(cmd_favorites, ["list", "--vault", vault_dir])
    assert "MY_KEY" in result.output


def test_cli_fav_remove(runner, vault_dir):
    add_favorite(vault_dir, "OLD_KEY")
    result = runner.invoke(cmd_favorites, ["remove", "OLD_KEY", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_cli_fav_check_is_favorite(runner, vault_dir):
    add_favorite(vault_dir, "PRESENT")
    result = runner.invoke(cmd_favorites, ["check", "PRESENT", "--vault", vault_dir])
    assert "is a favorite" in result.output

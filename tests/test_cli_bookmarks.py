import pytest
from click.testing import CliRunner
from envault.cli_bookmarks import cmd_bookmark
from envault.env_bookmarks import add_bookmark


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_bm_add_success(runner, vault_dir):
    result = runner.invoke(cmd_bookmark, ["add", "DB_URL", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "Bookmarked" in result.output


def test_bm_add_with_note(runner, vault_dir):
    result = runner.invoke(cmd_bookmark, ["add", "API_KEY", "--note", "secret", "--vault", vault_dir])
    assert result.exit_code == 0


def test_bm_list_empty(runner, vault_dir):
    result = runner.invoke(cmd_bookmark, ["list", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "No bookmarks" in result.output


def test_bm_list_shows_entries(runner, vault_dir):
    add_bookmark(vault_dir, "TOKEN", note="auth token")
    result = runner.invoke(cmd_bookmark, ["list", "--vault", vault_dir])
    assert "TOKEN" in result.output
    assert "auth token" in result.output


def test_bm_get_success(runner, vault_dir):
    add_bookmark(vault_dir, "SECRET", note="my note")
    result = runner.invoke(cmd_bookmark, ["get", "SECRET", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "my note" in result.output


def test_bm_get_missing(runner, vault_dir):
    result = runner.invoke(cmd_bookmark, ["get", "MISSING", "--vault", vault_dir])
    assert result.exit_code != 0


def test_bm_remove_success(runner, vault_dir):
    add_bookmark(vault_dir, "X")
    result = runner.invoke(cmd_bookmark, ["remove", "X", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_bm_remove_missing(runner, vault_dir):
    result = runner.invoke(cmd_bookmark, ["remove", "NOPE", "--vault", vault_dir])
    assert result.exit_code != 0


def test_bm_check_bookmarked(runner, vault_dir):
    add_bookmark(vault_dir, "FOO")
    result = runner.invoke(cmd_bookmark, ["check", "FOO", "--vault", vault_dir])
    assert "is bookmarked" in result.output


def test_bm_check_not_bookmarked(runner, vault_dir):
    result = runner.invoke(cmd_bookmark, ["check", "BAR", "--vault", vault_dir])
    assert "not bookmarked" in result.output

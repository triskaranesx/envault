import pytest
from click.testing import CliRunner
from envault.cli_comments import cmd_comments
from envault.env_comments import set_comment


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_comment_set_success(runner, vault_dir):
    result = runner.invoke(cmd_comments, ["set", "MY_KEY", "a note", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "Comment set" in result.output


def test_comment_get_shows_value(runner, vault_dir):
    set_comment(vault_dir, "MY_KEY", "hello world")
    result = runner.invoke(cmd_comments, ["get", "MY_KEY", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "hello world" in result.output


def test_comment_get_not_set(runner, vault_dir):
    result = runner.invoke(cmd_comments, ["get", "MISSING", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No comment" in result.output


def test_comment_remove_success(runner, vault_dir):
    set_comment(vault_dir, "MY_KEY", "bye")
    result = runner.invoke(cmd_comments, ["remove", "MY_KEY", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_comment_remove_missing(runner, vault_dir):
    result = runner.invoke(cmd_comments, ["remove", "GHOST", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No comment found" in result.output


def test_comment_list_empty(runner, vault_dir):
    result = runner.invoke(cmd_comments, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No comments" in result.output


def test_comment_list_shows_entries(runner, vault_dir):
    set_comment(vault_dir, "AAA", "first")
    set_comment(vault_dir, "BBB", "second")
    result = runner.invoke(cmd_comments, ["list", "--vault-dir", vault_dir])
    assert "AAA" in result.output
    assert "first" in result.output
    assert "BBB" in result.output

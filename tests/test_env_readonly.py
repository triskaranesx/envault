"""Tests for env_readonly module."""

import pytest
from click.testing import CliRunner
from envault.env_readonly import (
    mark_readonly, unmark_readonly, is_readonly, list_readonly,
    assert_writable, ReadOnlyError
)
from envault.cli_readonly import cmd_readonly


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def runner():
    return CliRunner()


def test_is_readonly_returns_false_when_absent(vault_dir):
    assert is_readonly(vault_dir, "MY_KEY") is False


def test_mark_and_check_readonly(vault_dir):
    mark_readonly(vault_dir, "MY_KEY")
    assert is_readonly(vault_dir, "MY_KEY") is True


def test_unmark_readonly(vault_dir):
    mark_readonly(vault_dir, "MY_KEY")
    unmark_readonly(vault_dir, "MY_KEY")
    assert is_readonly(vault_dir, "MY_KEY") is False


def test_unmark_nonexistent_does_not_raise(vault_dir):
    unmark_readonly(vault_dir, "GHOST")  # should not raise


def test_list_readonly_empty(vault_dir):
    assert list_readonly(vault_dir) == []


def test_list_readonly_returns_marked(vault_dir):
    mark_readonly(vault_dir, "A")
    mark_readonly(vault_dir, "B")
    result = list_readonly(vault_dir)
    assert "A" in result
    assert "B" in result


def test_assert_writable_passes_when_not_readonly(vault_dir):
    assert_writable(vault_dir, "MY_KEY")  # no exception


def test_assert_writable_raises_when_readonly(vault_dir):
    mark_readonly(vault_dir, "MY_KEY")
    with pytest.raises(ReadOnlyError):
        assert_writable(vault_dir, "MY_KEY")


def test_mark_empty_label_raises(vault_dir):
    with pytest.raises(ValueError):
        mark_readonly(vault_dir, "")


def test_cli_set_and_list(runner, vault_dir):
    result = runner.invoke(cmd_readonly, ["set", "DB_PASS", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "read-only" in result.output

    result = runner.invoke(cmd_readonly, ["list", "--vault", vault_dir])
    assert "DB_PASS" in result.output


def test_cli_check_writable(runner, vault_dir):
    result = runner.invoke(cmd_readonly, ["check", "MY_KEY", "--vault", vault_dir])
    assert "writable" in result.output


def test_cli_unset(runner, vault_dir):
    runner.invoke(cmd_readonly, ["set", "X", "--vault", vault_dir])
    result = runner.invoke(cmd_readonly, ["unset", "X", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "writable" in result.output

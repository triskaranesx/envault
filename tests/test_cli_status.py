"""Tests for envault/cli_status.py"""

import pytest
from click.testing import CliRunner
from envault.cli_status import cmd_status
from envault.env_status import set_status


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_status_set_success(runner, vault_dir):
    result = runner.invoke(cmd_status, ["set", "MY_KEY", "active", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "active" in result.output


def test_status_set_invalid_choice(runner, vault_dir):
    result = runner.invoke(cmd_status, ["set", "MY_KEY", "bogus", "--vault", vault_dir])
    assert result.exit_code != 0


def test_status_get_shows_value(runner, vault_dir):
    set_status(vault_dir, "MY_KEY", "deprecated")
    result = runner.invoke(cmd_status, ["get", "MY_KEY", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "deprecated" in result.output


def test_status_get_not_set(runner, vault_dir):
    result = runner.invoke(cmd_status, ["get", "MISSING", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "No status" in result.output


def test_status_remove_success(runner, vault_dir):
    set_status(vault_dir, "MY_KEY", "stable")
    result = runner.invoke(cmd_status, ["remove", "MY_KEY", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_status_remove_not_found(runner, vault_dir):
    result = runner.invoke(cmd_status, ["remove", "GHOST", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "No status found" in result.output


def test_status_list_empty(runner, vault_dir):
    result = runner.invoke(cmd_status, ["list", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "No statuses" in result.output


def test_status_list_shows_entries(runner, vault_dir):
    set_status(vault_dir, "KEY_A", "active")
    set_status(vault_dir, "KEY_B", "experimental")
    result = runner.invoke(cmd_status, ["list", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "KEY_A" in result.output
    assert "active" in result.output
    assert "KEY_B" in result.output
    assert "experimental" in result.output


def test_status_find_returns_matching(runner, vault_dir):
    set_status(vault_dir, "KEY_A", "stable")
    set_status(vault_dir, "KEY_B", "active")
    result = runner.invoke(cmd_status, ["find", "stable", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "KEY_A" in result.output
    assert "KEY_B" not in result.output


def test_status_find_no_matches(runner, vault_dir):
    result = runner.invoke(cmd_status, ["find", "deprecated", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "No labels" in result.output

"""Tests for envault.cli_pin CLI commands."""

import pytest
from click.testing import CliRunner
from envault.cli_pin import cmd_pin
from envault.env_pin import pin_entry


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_pin_set_success(runner, vault_dir):
    result = runner.invoke(cmd_pin, ["set", "MY_KEY", "abc", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "Pinned 'MY_KEY'" in result.output


def test_pin_get_shows_value(runner, vault_dir):
    pin_entry(vault_dir, "MY_KEY", "hello")
    result = runner.invoke(cmd_pin, ["get", "MY_KEY", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "MY_KEY=hello" in result.output


def test_pin_get_not_set(runner, vault_dir):
    result = runner.invoke(cmd_pin, ["get", "MISSING", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "No pin" in result.output


def test_pin_remove_existing(runner, vault_dir):
    pin_entry(vault_dir, "MY_KEY", "val")
    result = runner.invoke(cmd_pin, ["remove", "MY_KEY", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_pin_remove_nonexistent(runner, vault_dir):
    result = runner.invoke(cmd_pin, ["remove", "GHOST", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "No pin found" in result.output


def test_pin_list_empty(runner, vault_dir):
    result = runner.invoke(cmd_pin, ["list", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "No pins" in result.output


def test_pin_list_shows_entries(runner, vault_dir):
    pin_entry(vault_dir, "A", "1")
    pin_entry(vault_dir, "B", "2")
    result = runner.invoke(cmd_pin, ["list", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "A = 1" in result.output
    assert "B = 2" in result.output

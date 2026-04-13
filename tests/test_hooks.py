"""Tests for envault.hooks and envault.cli_hooks."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_hooks import cmd_hooks
from envault.hooks import (
    get_hook,
    list_hooks,
    remove_hook,
    run_hook,
    set_hook,
)


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture()
def runner():
    return CliRunner()


# --- unit tests ---

def test_set_and_get_hook(vault_dir):
    set_hook(vault_dir, "post-add", "echo hello")
    assert get_hook(vault_dir, "post-add") == "echo hello"


def test_get_hook_returns_none_when_absent(vault_dir):
    assert get_hook(vault_dir, "pre-get") is None


def test_set_hook_invalid_event_raises(vault_dir):
    with pytest.raises(ValueError, match="Unknown event"):
        set_hook(vault_dir, "on-launch", "echo bad")


def test_set_hook_empty_command_raises(vault_dir):
    with pytest.raises(ValueError, match="must not be empty"):
        set_hook(vault_dir, "pre-add", "   ")


def test_set_hook_overwrites_existing(vault_dir):
    set_hook(vault_dir, "pre-add", "echo first")
    set_hook(vault_dir, "pre-add", "echo second")
    assert get_hook(vault_dir, "pre-add") == "echo second"


def test_remove_hook_returns_true_when_present(vault_dir):
    set_hook(vault_dir, "post-rotate", "echo done")
    assert remove_hook(vault_dir, "post-rotate") is True
    assert get_hook(vault_dir, "post-rotate") is None


def test_remove_hook_returns_false_when_absent(vault_dir):
    assert remove_hook(vault_dir, "post-rotate") is False


def test_list_hooks_empty(vault_dir):
    assert list_hooks(vault_dir) == {}


def test_list_hooks_returns_all(vault_dir):
    set_hook(vault_dir, "pre-add", "echo a")
    set_hook(vault_dir, "post-get", "echo b")
    result = list_hooks(vault_dir)
    assert result == {"pre-add": "echo a", "post-get": "echo b"}


def test_run_hook_returns_none_when_absent(vault_dir):
    assert run_hook(vault_dir, "pre-add") is None


def test_run_hook_success_returns_zero(vault_dir):
    set_hook(vault_dir, "post-add", "true")
    assert run_hook(vault_dir, "post-add") == 0


def test_run_hook_failure_raises(vault_dir):
    set_hook(vault_dir, "pre-rotate", "false")
    with pytest.raises(RuntimeError, match="failed with exit code"):
        run_hook(vault_dir, "pre-rotate")


# --- CLI tests ---

def test_cli_hook_set(runner, vault_dir):
    result = runner.invoke(cmd_hooks, ["set", "post-add", "echo hi", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "Hook set" in result.output


def test_cli_hook_get_shows_command(runner, vault_dir):
    set_hook(vault_dir, "pre-get", "echo pre")
    result = runner.invoke(cmd_hooks, ["get", "pre-get", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "echo pre" in result.output


def test_cli_hook_get_missing(runner, vault_dir):
    result = runner.invoke(cmd_hooks, ["get", "pre-get", "--vault-dir", vault_dir])
    assert "No hook registered" in result.output


def test_cli_hook_remove(runner, vault_dir):
    set_hook(vault_dir, "post-rotate", "echo r")
    result = runner.invoke(cmd_hooks, ["remove", "post-rotate", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_cli_hook_list_empty(runner, vault_dir):
    result = runner.invoke(cmd_hooks, ["list", "--vault-dir", vault_dir])
    assert "No hooks" in result.output


def test_cli_hook_list_shows_entries(runner, vault_dir):
    set_hook(vault_dir, "pre-add", "lint .env")
    result = runner.invoke(cmd_hooks, ["list", "--vault-dir", vault_dir])
    assert "pre-add" in result.output
    assert "lint .env" in result.output

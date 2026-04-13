"""Tests for the CLI permissions commands."""

import pytest
from click.testing import CliRunner
from envault.cli_permissions import cmd_permissions
from envault.permissions import set_permission, get_permission


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_perm_set_success(runner, vault_dir):
    result = runner.invoke(cmd_permissions, ["set", "alice", "read", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "read" in result.output
    assert "alice" in result.output


def test_perm_set_invalid_role(runner, vault_dir):
    result = runner.invoke(cmd_permissions, ["set", "alice", "superuser", "--vault-dir", vault_dir])
    assert result.exit_code != 0


def test_perm_set_with_label(runner, vault_dir):
    result = runner.invoke(
        cmd_permissions, ["set", "bob", "write", "--vault-dir", vault_dir, "--label", "API_KEY"]
    )
    assert result.exit_code == 0
    assert "API_KEY" in result.output


def test_perm_get_existing(runner, vault_dir):
    set_permission(vault_dir, "alice", "admin")
    result = runner.invoke(cmd_permissions, ["get", "alice", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "admin" in result.output


def test_perm_get_missing(runner, vault_dir):
    result = runner.invoke(cmd_permissions, ["get", "ghost", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No permission" in result.output


def test_perm_remove_existing(runner, vault_dir):
    set_permission(vault_dir, "alice", "read")
    result = runner.invoke(cmd_permissions, ["remove", "alice", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "Removed" in result.output
    assert get_permission(vault_dir, "alice") is None


def test_perm_remove_missing(runner, vault_dir):
    result = runner.invoke(cmd_permissions, ["remove", "ghost", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No permission" in result.output


def test_perm_list_empty(runner, vault_dir):
    result = runner.invoke(cmd_permissions, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No permissions" in result.output


def test_perm_list_shows_entries(runner, vault_dir):
    set_permission(vault_dir, "alice", "admin")
    set_permission(vault_dir, "bob", "read")
    result = runner.invoke(cmd_permissions, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "alice" in result.output
    assert "bob" in result.output


def test_perm_list_with_label_filter(runner, vault_dir):
    set_permission(vault_dir, "carol", "write", label="DB_URL")
    set_permission(vault_dir, "dave", "read")
    result = runner.invoke(
        cmd_permissions, ["list", "--vault-dir", vault_dir, "--label", "DB_URL"]
    )
    assert result.exit_code == 0
    assert "carol" in result.output
    assert "dave" not in result.output

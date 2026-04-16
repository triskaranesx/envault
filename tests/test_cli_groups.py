"""Tests for envault.cli_groups."""
import pytest
from click.testing import CliRunner
from envault.cli_groups import cmd_group
from envault.env_groups import add_label_to_group, create_group


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_group_create(runner, vault_dir):
    result = runner.invoke(cmd_group, ["create", "backend", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "created" in result.output


def test_group_list_empty(runner, vault_dir):
    result = runner.invoke(cmd_group, ["list", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "No groups" in result.output


def test_group_list_shows_groups(runner, vault_dir):
    create_group(vault_dir, "alpha")
    result = runner.invoke(cmd_group, ["list", "--vault", vault_dir])
    assert "alpha" in result.output


def test_group_add_and_show(runner, vault_dir):
    runner.invoke(cmd_group, ["add", "grp", "DB_URL", "--vault", vault_dir])
    result = runner.invoke(cmd_group, ["show", "grp", "--vault", vault_dir])
    assert "DB_URL" in result.output


def test_group_show_nonexistent(runner, vault_dir):
    result = runner.invoke(cmd_group, ["show", "ghost", "--vault", vault_dir])
    assert result.exit_code != 0


def test_group_remove_label(runner, vault_dir):
    add_label_to_group(vault_dir, "grp", "KEY")
    runner.invoke(cmd_group, ["remove", "grp", "KEY", "--vault", vault_dir])
    result = runner.invoke(cmd_group, ["show", "grp", "--vault", vault_dir])
    assert "KEY" not in result.output


def test_group_delete(runner, vault_dir):
    create_group(vault_dir, "tmp")
    runner.invoke(cmd_group, ["delete", "tmp", "--vault", vault_dir])
    result = runner.invoke(cmd_group, ["list", "--vault", vault_dir])
    assert "tmp" not in result.output


def test_group_find(runner, vault_dir):
    add_label_to_group(vault_dir, "a", "X")
    add_label_to_group(vault_dir, "b", "X")
    result = runner.invoke(cmd_group, ["find", "X", "--vault", vault_dir])
    assert "a" in result.output
    assert "b" in result.output


def test_group_find_not_in_any(runner, vault_dir):
    result = runner.invoke(cmd_group, ["find", "NOPE", "--vault", vault_dir])
    assert "not in any group" in result.output

"""Tests for envault/cli_category.py"""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_category import cmd_category
from envault.env_category import set_category


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_category_set_success(runner, vault_dir):
    result = runner.invoke(
        cmd_category, ["set", "MY_KEY", "database", "--vault", vault_dir]
    )
    assert result.exit_code == 0
    assert "database" in result.output
    assert "MY_KEY" in result.output


def test_category_set_invalid_chars_fails(runner, vault_dir):
    result = runner.invoke(
        cmd_category, ["set", "MY_KEY", "bad cat!", "--vault", vault_dir]
    )
    assert result.exit_code != 0
    assert "invalid characters" in result.output


def test_category_get_shows_value(runner, vault_dir):
    set_category(vault_dir, "MY_KEY", "auth")
    result = runner.invoke(cmd_category, ["get", "MY_KEY", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "auth" in result.output


def test_category_get_not_set(runner, vault_dir):
    result = runner.invoke(cmd_category, ["get", "MISSING", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "No category" in result.output


def test_category_remove_success(runner, vault_dir):
    set_category(vault_dir, "MY_KEY", "auth")
    result = runner.invoke(cmd_category, ["remove", "MY_KEY", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_category_remove_not_set(runner, vault_dir):
    result = runner.invoke(cmd_category, ["remove", "MISSING", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "No category was set" in result.output


def test_category_list_empty(runner, vault_dir):
    result = runner.invoke(cmd_category, ["list", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "No categories" in result.output


def test_category_list_shows_entries(runner, vault_dir):
    set_category(vault_dir, "A", "auth")
    set_category(vault_dir, "B", "database")
    result = runner.invoke(cmd_category, ["list", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "A: auth" in result.output
    assert "B: database" in result.output


def test_category_find_returns_matching(runner, vault_dir):
    set_category(vault_dir, "A", "auth")
    set_category(vault_dir, "B", "database")
    result = runner.invoke(cmd_category, ["find", "auth", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "A" in result.output
    assert "B" not in result.output


def test_category_find_no_match(runner, vault_dir):
    result = runner.invoke(cmd_category, ["find", "nonexistent", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "No labels found" in result.output

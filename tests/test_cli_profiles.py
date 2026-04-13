"""Tests for envault/cli_profiles.py"""

import pytest
from click.testing import CliRunner
from envault.cli_profiles import cmd_profile


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_profile_save_success(runner, vault_dir):
    result = runner.invoke(
        cmd_profile, ["save", "prod", "DB_URL", "API_KEY", "--vault-dir", vault_dir]
    )
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "2 label" in result.output


def test_profile_save_empty_name_fails(runner, vault_dir):
    # Click won't allow empty string as argument easily; test empty labels instead
    result = runner.invoke(
        cmd_profile, ["save", "prod", "--vault-dir", vault_dir]
    )
    assert result.exit_code != 0


def test_profile_show_success(runner, vault_dir):
    runner.invoke(cmd_profile, ["save", "dev", "DEBUG", "LOG_LEVEL", "--vault-dir", vault_dir])
    result = runner.invoke(cmd_profile, ["show", "dev", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "DEBUG" in result.output
    assert "LOG_LEVEL" in result.output


def test_profile_show_missing(runner, vault_dir):
    result = runner.invoke(cmd_profile, ["show", "ghost", "--vault-dir", vault_dir])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_profile_delete_success(runner, vault_dir):
    runner.invoke(cmd_profile, ["save", "staging", "S3_BUCKET", "--vault-dir", vault_dir])
    result = runner.invoke(cmd_profile, ["delete", "staging", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_profile_delete_missing(runner, vault_dir):
    result = runner.invoke(cmd_profile, ["delete", "nope", "--vault-dir", vault_dir])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_profile_list_empty(runner, vault_dir):
    result = runner.invoke(cmd_profile, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No profiles" in result.output


def test_profile_list_shows_names(runner, vault_dir):
    runner.invoke(cmd_profile, ["save", "prod", "A", "--vault-dir", vault_dir])
    runner.invoke(cmd_profile, ["save", "dev", "B", "--vault-dir", vault_dir])
    result = runner.invoke(cmd_profile, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "dev" in result.output

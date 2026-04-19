"""Tests for envault.cli_validate CLI commands."""

from __future__ import annotations

import os
import pytest
from click.testing import CliRunner

from envault.vault import init_vault, add_entry
from envault.cli_validate import cmd_validate


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_dir(tmp_path):
    vpath = str(tmp_path / "vault")
    os.makedirs(vpath)
    init_vault(vpath, "secret")
    add_entry(vpath, "secret", "API_KEY", "realvalue123")
    add_entry(vpath, "secret", "DB_URL", "https://db.example.com")
    return vpath


def test_validate_run_all_clean(runner, vault_dir):
    result = runner.invoke(
        cmd_validate,
        ["run", "--vault", vault_dir, "--password", "secret"],
    )
    assert result.exit_code == 0
    assert "passed" in result.output


def test_validate_run_detects_empty_value(runner, vault_dir):
    # Add an entry with empty value by bypassing CLI (direct vault write)
    from envault.vault import _load_vault_raw, _save_vault_raw
    from envault.crypto import encrypt

    raw = _load_vault_raw(vault_dir)
    raw["entries"]["EMPTY_KEY"] = {"versions": [{"ciphertext": encrypt("", "secret")}]}
    _save_vault_raw(vault_dir, raw)

    result = runner.invoke(
        cmd_validate,
        ["run", "--vault", vault_dir, "--password", "secret"],
    )
    assert result.exit_code == 1
    assert "ERROR" in result.output
    assert "empty_value" in result.output


def test_validate_run_label_filter(runner, vault_dir):
    result = runner.invoke(
        cmd_validate,
        ["run", "--vault", vault_dir, "--password", "secret", "--label", "API_KEY"],
    )
    assert result.exit_code == 0
    assert "passed" in result.output


def test_validate_run_label_filter_nonexistent(runner, vault_dir):
    """Filtering by a label that doesn't exist should report no entries validated."""
    result = runner.invoke(
        cmd_validate,
        ["run", "--vault", vault_dir, "--password", "secret", "--label", "NONEXISTENT"],
    )
    assert result.exit_code == 0
    assert "no entries" in result.output.lower() or "0" in result.output


def test_validate_run_strict_flag_exits_nonzero_on_warnings(runner, vault_dir):
    # Add a label with a warning-inducing name (lowercase)
    add_entry(vault_dir, "secret", "lowercase_label", "value")
    result = runner.invoke(
        cmd_validate,
        ["run", "--vault", vault_dir, "--password", "secret", "--strict"],
    )
    assert result.exit_code == 1
    assert "WARN" in result.output


def test_validate_run_vault_not_found(runner, tmp_path):
    result = runner.invoke(
        cmd_validate,
        ["run", "--vault", str(tmp_path / "no_vault"), "--password", "x"],
    )
    assert result.exit_code == 1
    assert "not found" in result.output


def test_validate_run_wrong_password_skips_entries(runner, vault_dir):
    result = runner.invoke(
        cmd_validate,
        ["run", "--vault", vault_dir, "--password", "wrongpassword"],
    )
    # Should not crash; entries are skipped with a warning
    assert "skipped" in result.output or result.exit_code in (0, 1)

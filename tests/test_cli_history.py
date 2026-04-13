"""Tests for cli_history commands."""

import pytest
from click.testing import CliRunner
from envault.cli_history import cmd_log, cmd_clear_log
from envault.history import record_change


@pytest.fixture
def runner():
    return CliRunner()


def test_log_empty(runner, tmp_path):
    result = runner.invoke(cmd_log, ["--vault-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "No history found" in result.output


def test_log_shows_entries(runner, tmp_path):
    record_change("API_KEY", 1, "add", vault_dir=str(tmp_path))
    result = runner.invoke(cmd_log, ["--vault-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "add" in result.output


def test_log_filter_by_label(runner, tmp_path):
    record_change("API_KEY", 1, "add", vault_dir=str(tmp_path))
    record_change("DB_URL", 1, "add", vault_dir=str(tmp_path))
    result = runner.invoke(
        cmd_log, ["--label", "API_KEY", "--vault-dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "DB_URL" not in result.output


def test_clear_log_wipes_history(runner, tmp_path):
    record_change("KEY", 1, "add", vault_dir=str(tmp_path))
    result = runner.invoke(
        cmd_clear_log, ["--vault-dir", str(tmp_path)], input="y\n"
    )
    assert result.exit_code == 0
    assert "cleared" in result.output.lower()
    check = runner.invoke(cmd_log, ["--vault-dir", str(tmp_path)])
    assert "No history found" in check.output


def test_clear_log_aborted(runner, tmp_path):
    record_change("KEY", 1, "add", vault_dir=str(tmp_path))
    result = runner.invoke(
        cmd_clear_log, ["--vault-dir", str(tmp_path)], input="n\n"
    )
    assert result.exit_code != 0 or "Aborted" in result.output
    check = runner.invoke(cmd_log, ["--vault-dir", str(tmp_path)])
    assert "KEY" in check.output

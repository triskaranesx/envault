"""Tests for envault.cli_expiry commands."""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_expiry import cmd_expiry


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_expiry_set_outputs_iso(runner, vault_dir):
    result = runner.invoke(cmd_expiry, ["set", "DB_PASS", "30", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "DB_PASS" in result.output
    assert "Expiry set" in result.output


def test_expiry_get_no_expiry(runner, vault_dir):
    result = runner.invoke(cmd_expiry, ["get", "MISSING", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "No expiry" in result.output


def test_expiry_get_shows_date(runner, vault_dir):
    runner.invoke(cmd_expiry, ["set", "API_KEY", "10", "--vault", vault_dir])
    result = runner.invoke(cmd_expiry, ["get", "API_KEY", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "API_KEY" in result.output


def test_expiry_get_shows_expired_flag(runner, tmp_path):
    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    (tmp_path / "expiry.json").write_text(json.dumps({"OLD": past}))
    result = runner.invoke(cmd_expiry, ["get", "OLD", "--vault", str(tmp_path)])
    assert result.exit_code == 0
    assert "EXPIRED" in result.output


def test_expiry_remove_existing(runner, vault_dir):
    runner.invoke(cmd_expiry, ["set", "TOKEN", "5", "--vault", vault_dir])
    result = runner.invoke(cmd_expiry, ["remove", "TOKEN", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_expiry_remove_missing(runner, vault_dir):
    result = runner.invoke(cmd_expiry, ["remove", "GHOST", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "No expiry was set" in result.output


def test_expiry_list_empty(runner, vault_dir):
    result = runner.invoke(cmd_expiry, ["list", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "No expiry dates set" in result.output


def test_expiry_list_shows_entries(runner, vault_dir):
    runner.invoke(cmd_expiry, ["set", "X", "3", "--vault", vault_dir])
    result = runner.invoke(cmd_expiry, ["list", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "X" in result.output


def test_expiry_list_expired_only(runner, tmp_path):
    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    future = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
    (tmp_path / "expiry.json").write_text(json.dumps({"OLD": past, "NEW": future}))
    result = runner.invoke(
        cmd_expiry, ["list", "--expired-only", "--vault", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "OLD" in result.output
    assert "NEW" not in result.output

"""Tests for CLI TTL commands."""
import pytest
import json
from pathlib import Path
from click.testing import CliRunner
from envault.cli_ttl import cmd_ttl


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_ttl_set_success(runner, vault_dir):
    result = runner.invoke(cmd_ttl, ["set", "MY_KEY", "300", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "MY_KEY" in result.output
    assert "expires at" in result.output


def test_ttl_set_invalid_seconds(runner, vault_dir):
    result = runner.invoke(cmd_ttl, ["set", "X", "-5", "--vault", vault_dir])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_ttl_get_not_set(runner, vault_dir):
    result = runner.invoke(cmd_ttl, ["get", "MISSING", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "No TTL set" in result.output


def test_ttl_get_shows_info(runner, vault_dir):
    runner.invoke(cmd_ttl, ["set", "DB", "600", "--vault", vault_dir])
    result = runner.invoke(cmd_ttl, ["get", "DB", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "DB" in result.output
    assert "expires at" in result.output.lower() or "Expires at" in result.output


def test_ttl_remove_existing(runner, vault_dir):
    runner.invoke(cmd_ttl, ["set", "TOKEN", "100", "--vault", vault_dir])
    result = runner.invoke(cmd_ttl, ["remove", "TOKEN", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_ttl_remove_nonexistent(runner, vault_dir):
    result = runner.invoke(cmd_ttl, ["remove", "GHOST", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "No TTL found" in result.output


def test_ttl_list_empty(runner, vault_dir):
    result = runner.invoke(cmd_ttl, ["list", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "No TTL" in result.output


def test_ttl_list_shows_entries(runner, vault_dir):
    runner.invoke(cmd_ttl, ["set", "A", "10", "--vault", vault_dir])
    runner.invoke(cmd_ttl, ["set", "B", "20", "--vault", vault_dir])
    result = runner.invoke(cmd_ttl, ["list", "--vault", vault_dir])
    assert "A" in result.output
    assert "B" in result.output


def test_ttl_list_expired_only(runner, vault_dir):
    runner.invoke(cmd_ttl, ["set", "LIVE", "9999", "--vault", vault_dir])
    runner.invoke(cmd_ttl, ["set", "DEAD", "1", "--vault", vault_dir])
    p = Path(vault_dir) / "ttl.json"
    data = json.loads(p.read_text())
    data["DEAD"]["expires_at"] = "2000-01-01T00:00:00+00:00"
    p.write_text(json.dumps(data))
    result = runner.invoke(cmd_ttl, ["list", "--expired-only", "--vault", vault_dir])
    assert "DEAD" in result.output
    assert "LIVE" not in result.output

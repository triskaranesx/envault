"""Tests for envault.cli_watch CLI commands."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_watch import cmd_watch
from envault.env_watch import update_fingerprint


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    vault = tmp_path / "vault.json"
    vault.write_text(json.dumps({"entries": [], "version": 1}))
    return tmp_path


def test_status_changed(runner: CliRunner, vault_dir: Path) -> None:
    result = runner.invoke(cmd_watch, ["status", str(vault_dir)])
    assert result.exit_code == 0
    assert "CHANGED" in result.output


def test_status_unchanged(runner: CliRunner, vault_dir: Path) -> None:
    update_fingerprint(vault_dir)
    result = runner.invoke(cmd_watch, ["status", str(vault_dir)])
    assert result.exit_code == 0
    assert "OK" in result.output


def test_status_missing_vault(runner: CliRunner, tmp_path: Path) -> None:
    result = runner.invoke(cmd_watch, ["status", str(tmp_path)])
    assert result.exit_code != 0
    assert "No vault" in result.output


def test_mark_records_fingerprint(runner: CliRunner, vault_dir: Path) -> None:
    result = runner.invoke(cmd_watch, ["mark", str(vault_dir)])
    assert result.exit_code == 0
    assert "Fingerprint recorded" in result.output


def test_mark_missing_vault(runner: CliRunner, tmp_path: Path) -> None:
    result = runner.invoke(cmd_watch, ["mark", str(tmp_path)])
    assert result.exit_code != 0


def test_once_detects_change(runner: CliRunner, vault_dir: Path) -> None:
    result = runner.invoke(cmd_watch, ["once", str(vault_dir)])
    assert result.exit_code == 0
    assert "Change detected" in result.output


def test_once_no_change(runner: CliRunner, vault_dir: Path) -> None:
    update_fingerprint(vault_dir)
    result = runner.invoke(cmd_watch, ["once", str(vault_dir)])
    assert result.exit_code == 0
    assert "No changes" in result.output

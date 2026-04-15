"""Integration tests for the rename CLI commands."""

from __future__ import annotations

import json
import os

import pytest
from click.testing import CliRunner

from envault.vault import init_vault, add_entry
from envault.cli_rename import cmd_rename


PASSWORD = "secret"


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_dir(tmp_path):
    vd = str(tmp_path)
    init_vault(vd, PASSWORD)
    add_entry(vd, PASSWORD, "API_KEY", "abc123")
    add_entry(vd, PASSWORD, "API_SECRET", "xyz789")
    return vd


def _labels(vault_dir: str) -> list[str]:
    data = json.loads(open(os.path.join(vault_dir, "vault.json")).read())
    return [e["label"] for e in data["entries"]]


# ---------------------------------------------------------------------------
# Success cases
# ---------------------------------------------------------------------------

def test_rename_run_success(runner, vault_dir):
    result = runner.invoke(
        cmd_rename,
        ["run", "API_KEY", "SERVICE_API_KEY", "--vault", vault_dir],
    )
    assert result.exit_code == 0, result.output
    assert "SERVICE_API_KEY" in result.output
    assert "SERVICE_API_KEY" in _labels(vault_dir)
    assert "API_KEY" not in _labels(vault_dir)


def test_rename_run_overwrite_flag(runner, vault_dir):
    result = runner.invoke(
        cmd_rename,
        ["run", "API_KEY", "API_SECRET", "--vault", vault_dir, "--overwrite"],
    )
    assert result.exit_code == 0, result.output
    assert _labels(vault_dir).count("API_SECRET") == 1


# ---------------------------------------------------------------------------
# Failure cases
# ---------------------------------------------------------------------------

def test_rename_run_missing_label(runner, vault_dir):
    result = runner.invoke(
        cmd_rename,
        ["run", "DOES_NOT_EXIST", "NEW_LABEL", "--vault", vault_dir],
    )
    assert result.exit_code != 0
    assert "not found" in result.output.lower() or "Error" in result.output


def test_rename_run_conflict_without_overwrite(runner, vault_dir):
    result = runner.invoke(
        cmd_rename,
        ["run", "API_KEY", "API_SECRET", "--vault", vault_dir],
    )
    assert result.exit_code != 0
    assert "already exists" in result.output or "Error" in result.output


def test_rename_run_identical_labels(runner, vault_dir):
    result = runner.invoke(
        cmd_rename,
        ["run", "API_KEY", "API_KEY", "--vault", vault_dir],
    )
    assert result.exit_code != 0

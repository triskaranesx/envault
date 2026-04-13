"""Tests for envault.cli_diff CLI commands."""

from __future__ import annotations

import json
import os

import pytest
from click.testing import CliRunner

from envault.cli_diff import cmd_diff
from envault.crypto import encrypt

PASSWORD = "cli-diff-pass"


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_dir(tmp_path: "pathlib.Path") -> str:
    entries = [
        {
            "label": "SECRET",
            "version": 1,
            "value": encrypt("old-value", PASSWORD),
        },
        {
            "label": "SECRET",
            "version": 2,
            "value": encrypt("new-value", PASSWORD),
        },
    ]
    vault_file = os.path.join(str(tmp_path), "vault.json")
    with open(vault_file, "w") as fh:
        json.dump({"version": 1, "entries": entries}, fh)
    return str(tmp_path)


def test_diff_show_changed(runner: CliRunner, vault_dir: str) -> None:
    result = runner.invoke(
        cmd_diff,
        ["show", "SECRET", "--vault", vault_dir, "--password", PASSWORD, "--v1", "1", "--v2", "2"],
    )
    assert result.exit_code == 0
    assert "CHANGED" in result.output
    assert "old-value" in result.output
    assert "new-value" in result.output


def test_diff_show_unchanged(runner: CliRunner, vault_dir: str) -> None:
    result = runner.invoke(
        cmd_diff,
        ["show", "SECRET", "--vault", vault_dir, "--password", PASSWORD, "--v1", "1", "--v2", "1"],
    )
    assert result.exit_code == 0
    assert "UNCHANGED" in result.output


def test_diff_versions_command(runner: CliRunner, vault_dir: str) -> None:
    result = runner.invoke(
        cmd_diff,
        ["versions", "SECRET", "--vault", vault_dir],
    )
    assert result.exit_code == 0
    assert "SECRET" in result.output
    assert "1" in result.output
    assert "2" in result.output


def test_diff_versions_unknown_label(runner: CliRunner, vault_dir: str) -> None:
    result = runner.invoke(
        cmd_diff,
        ["versions", "NOPE", "--vault", vault_dir],
    )
    assert result.exit_code == 0
    assert "No entries found" in result.output

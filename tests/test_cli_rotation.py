"""CLI tests for the rotate command."""

from __future__ import annotations

import pytest
from pathlib import Path
from click.testing import CliRunner

from envault.cli_rotation import cmd_rotate
from envault.vault import init_vault, add_entry


OLD = "old-secret"
NEW = "new-secret"


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    vdir = tmp_path / ".envault"
    init_vault(vdir)
    add_entry(vdir, "TOKEN", "abc123", OLD)
    return vdir


def test_rotate_all_success(runner: CliRunner, vault_dir: Path) -> None:
    result = runner.invoke(
        cmd_rotate,
        ["--vault", str(vault_dir), "--old-password", OLD, "--new-password", NEW],
    )
    assert result.exit_code == 0
    assert "Rotated 1 entries" in result.output


def test_rotate_single_label(runner: CliRunner, vault_dir: Path) -> None:
    result = runner.invoke(
        cmd_rotate,
        ["--vault", str(vault_dir), "--label", "TOKEN",
         "--old-password", OLD, "--new-password", NEW],
    )
    assert result.exit_code == 0
    assert "Rotated entry 'TOKEN'" in result.output


def test_rotate_missing_label(runner: CliRunner, vault_dir: Path) -> None:
    result = runner.invoke(
        cmd_rotate,
        ["--vault", str(vault_dir), "--label", "NOPE",
         "--old-password", OLD, "--new-password", NEW],
    )
    assert result.exit_code != 0
    assert "not found" in result.output


def test_rotate_wrong_old_password(runner: CliRunner, vault_dir: Path) -> None:
    result = runner.invoke(
        cmd_rotate,
        ["--vault", str(vault_dir), "--old-password", "wrong", "--new-password", NEW],
    )
    assert result.exit_code != 0
    assert "failed" in result.output.lower()


def test_rotate_same_password_rejected(runner: CliRunner, vault_dir: Path) -> None:
    result = runner.invoke(
        cmd_rotate,
        ["--vault", str(vault_dir), "--old-password", OLD, "--new-password", OLD],
    )
    assert result.exit_code != 0
    assert "differ" in result.output


def test_rotate_vault_not_found(runner: CliRunner, tmp_path: Path) -> None:
    result = runner.invoke(
        cmd_rotate,
        ["--vault", str(tmp_path / "missing"), "--old-password", OLD, "--new-password", NEW],
    )
    assert result.exit_code != 0
    assert "not found" in result.output

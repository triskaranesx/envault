"""Tests for the import-env CLI command."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_import import cmd_import_env
from envault.vault import get_entry, init_vault


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner(mix_stderr=False)


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    content = textwrap.dedent("""\
        KEY_A=value_a
        KEY_B=value_b
    """)
    p = tmp_path / ".env"
    p.write_text(content)
    return p


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    v = tmp_path / "vault.json"
    init_vault(v, "secret")
    return v


def test_import_env_success(runner: CliRunner, env_file: Path, vault_path: Path) -> None:
    result = runner.invoke(
        cmd_import_env,
        [str(env_file), "--vault", str(vault_path), "--password", "secret"],
    )
    assert result.exit_code == 0
    assert "Imported 2" in result.output
    assert "skipped 0" in result.output


def test_import_env_creates_entries(runner: CliRunner, env_file: Path, tmp_path: Path) -> None:
    vault = tmp_path / "v.json"
    runner.invoke(
        cmd_import_env,
        [str(env_file), "--vault", str(vault), "--password", "pw"],
    )
    assert get_entry(vault, "KEY_A", "pw") == "value_a"


def test_import_env_with_prefix(runner: CliRunner, env_file: Path, tmp_path: Path) -> None:
    vault = tmp_path / "v.json"
    runner.invoke(
        cmd_import_env,
        [str(env_file), "--vault", str(vault), "--password", "pw", "--prefix", "dev"],
    )
    assert get_entry(vault, "dev.KEY_A", "pw") == "value_a"


def test_import_env_skip_duplicates(runner: CliRunner, env_file: Path, vault_path: Path) -> None:
    runner.invoke(
        cmd_import_env,
        [str(env_file), "--vault", str(vault_path), "--password", "secret"],
    )
    result = runner.invoke(
        cmd_import_env,
        [str(env_file), "--vault", str(vault_path), "--password", "secret"],
    )
    assert "skipped 2" in result.output


def test_import_env_overwrite_flag(runner: CliRunner, env_file: Path, vault_path: Path) -> None:
    runner.invoke(
        cmd_import_env,
        [str(env_file), "--vault", str(vault_path), "--password", "secret"],
    )
    result = runner.invoke(
        cmd_import_env,
        [
            str(env_file), "--vault", str(vault_path),
            "--password", "secret", "--overwrite",
        ],
    )
    assert result.exit_code == 0
    assert "Imported 2" in result.output

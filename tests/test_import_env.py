"""Tests for envault.import_env."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from envault.import_env import parse_env_file, import_env_file
from envault.vault import get_entry, init_vault


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    content = textwrap.dedent("""\
        # a comment
        DB_HOST=localhost
        DB_PORT=5432
        APP_SECRET="super secret"
        GREETING='hello world'
        export PATH_OVERRIDE=/usr/local/bin
    """)
    p = tmp_path / ".env"
    p.write_text(content)
    return p


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    vault = tmp_path / "vault.json"
    init_vault(vault, "pw")
    return vault


def test_parse_env_file_returns_pairs(env_file: Path) -> None:
    pairs = parse_env_file(env_file)
    assert ("DB_HOST", "localhost") in pairs
    assert ("DB_PORT", "5432") in pairs


def test_parse_env_file_strips_quotes(env_file: Path) -> None:
    pairs = dict(parse_env_file(env_file))
    assert pairs["APP_SECRET"] == "super secret"
    assert pairs["GREETING"] == "hello world"


def test_parse_env_file_handles_export(env_file: Path) -> None:
    pairs = dict(parse_env_file(env_file))
    assert "PATH_OVERRIDE" in pairs
    assert pairs["PATH_OVERRIDE"] == "/usr/local/bin"


def test_parse_env_file_ignores_comments(env_file: Path) -> None:
    pairs = parse_env_file(env_file)
    keys = [k for k, _ in pairs]
    assert all(not k.startswith("#") for k in keys)


def test_import_env_file_imports_all(env_file: Path, tmp_path: Path) -> None:
    vault = tmp_path / "vault.json"
    result = import_env_file(vault, env_file, "pw")
    assert result["imported"] == 5
    assert result["skipped"] == 0


def test_import_env_file_skips_existing(env_file: Path, tmp_path: Path) -> None:
    vault = tmp_path / "vault.json"
    import_env_file(vault, env_file, "pw")
    result = import_env_file(vault, env_file, "pw", overwrite=False)
    assert result["skipped"] == 5
    assert result["imported"] == 0


def test_import_env_file_overwrite(env_file: Path, tmp_path: Path) -> None:
    vault = tmp_path / "vault.json"
    import_env_file(vault, env_file, "pw")
    result = import_env_file(vault, env_file, "pw", overwrite=True)
    assert result["imported"] == 5


def test_import_env_file_with_prefix(env_file: Path, tmp_path: Path) -> None:
    vault = tmp_path / "vault.json"
    import_env_file(vault, env_file, "pw", prefix="staging")
    value = get_entry(vault, "staging.DB_HOST", "pw")
    assert value == "localhost"


def test_import_creates_vault_if_missing(env_file: Path, tmp_path: Path) -> None:
    vault = tmp_path / "new_vault.json"
    assert not vault.exists()
    import_env_file(vault, env_file, "pw")
    assert vault.exists()

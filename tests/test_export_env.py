"""Tests for envault.export_env module."""

from __future__ import annotations

import os
import pytest
from pathlib import Path

from envault.vault import init_vault, add_entry
from envault.export_env import export_env


PASSWORD = "test-secret-pw"


@pytest.fixture()
def vault_dir(tmp_path: Path) -> str:
    vdir = str(tmp_path / "vault")
    init_vault(vdir, PASSWORD)
    add_entry(vdir, "DB_HOST", "localhost", PASSWORD)
    add_entry(vdir, "DB_PORT", "5432", PASSWORD)
    add_entry(vdir, "API_KEY", "abc def", PASSWORD)  # contains space → quoted
    return vdir


def test_export_returns_string(vault_dir: str) -> None:
    result = export_env(vault_dir, PASSWORD)
    assert isinstance(result, str)
    assert len(result) > 0


def test_export_contains_all_labels(vault_dir: str) -> None:
    result = export_env(vault_dir, PASSWORD)
    assert "DB_HOST=localhost" in result
    assert "DB_PORT=5432" in result


def test_export_quotes_values_with_spaces(vault_dir: str) -> None:
    result = export_env(vault_dir, PASSWORD)
    assert 'API_KEY="abc def"' in result


def test_export_filter_by_label(vault_dir: str) -> None:
    result = export_env(vault_dir, PASSWORD, label_filter=["DB_HOST"])
    assert "DB_HOST=localhost" in result
    assert "DB_PORT" not in result
    assert "API_KEY" not in result


def test_export_missing_label_raises(vault_dir: str) -> None:
    with pytest.raises(ValueError, match="not found"):
        export_env(vault_dir, PASSWORD, label_filter=["NONEXISTENT"])


def test_export_wrong_password_raises(vault_dir: str) -> None:
    with pytest.raises(Exception):
        export_env(vault_dir, "wrong-password")


def test_export_writes_file(vault_dir: str, tmp_path: Path) -> None:
    out_file = str(tmp_path / ".env")
    content = export_env(vault_dir, PASSWORD, output_path=out_file)
    assert Path(out_file).exists()
    assert Path(out_file).read_text(encoding="utf-8") == content


def test_export_empty_vault_raises(tmp_path: Path) -> None:
    vdir = str(tmp_path / "empty_vault")
    init_vault(vdir, PASSWORD)
    with pytest.raises(ValueError, match="empty"):
        export_env(vdir, PASSWORD)


def test_export_ends_with_newline(vault_dir: str) -> None:
    result = export_env(vault_dir, PASSWORD)
    assert result.endswith("\n")

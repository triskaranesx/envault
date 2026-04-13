"""Tests for envault.rotation."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.vault import init_vault, add_entry, get_entry
from envault.rotation import rotate_password, rotate_entry
from envault.crypto import decrypt


OLD_PASS = "old-secret"
NEW_PASS = "new-secret"


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    vdir = tmp_path / ".envault"
    init_vault(vdir)
    return vdir


@pytest.fixture()
def populated_vault(vault_dir: Path) -> Path:
    add_entry(vault_dir, "DB_URL", "postgres://localhost/db", OLD_PASS)
    add_entry(vault_dir, "API_KEY", "supersecret123", OLD_PASS)
    return vault_dir


def test_rotate_password_returns_count(populated_vault: Path) -> None:
    count = rotate_password(populated_vault, OLD_PASS, NEW_PASS)
    assert count == 2


def test_rotate_password_new_password_works(populated_vault: Path) -> None:
    rotate_password(populated_vault, OLD_PASS, NEW_PASS)
    value = get_entry(populated_vault, "DB_URL", NEW_PASS)
    assert value == "postgres://localhost/db"


def test_rotate_password_old_password_fails(populated_vault: Path) -> None:
    rotate_password(populated_vault, OLD_PASS, NEW_PASS)
    with pytest.raises(Exception):
        get_entry(populated_vault, "DB_URL", OLD_PASS)


def test_rotate_password_wrong_old_raises(populated_vault: Path) -> None:
    with pytest.raises(ValueError):
        rotate_password(populated_vault, "wrong-pass", NEW_PASS)


def test_rotate_entry_returns_true_when_found(populated_vault: Path) -> None:
    result = rotate_entry(populated_vault, "API_KEY", OLD_PASS, NEW_PASS)
    assert result is True


def test_rotate_entry_returns_false_when_missing(populated_vault: Path) -> None:
    result = rotate_entry(populated_vault, "MISSING_KEY", OLD_PASS, NEW_PASS)
    assert result is False


def test_rotate_entry_only_affects_target(populated_vault: Path) -> None:
    rotate_entry(populated_vault, "API_KEY", OLD_PASS, NEW_PASS)
    # DB_URL still encrypted with old password
    value = get_entry(populated_vault, "DB_URL", OLD_PASS)
    assert value == "postgres://localhost/db"
    # API_KEY now uses new password
    value2 = get_entry(populated_vault, "API_KEY", NEW_PASS)
    assert value2 == "supersecret123"


def test_rotate_empty_vault_returns_zero(vault_dir: Path) -> None:
    count = rotate_password(vault_dir, OLD_PASS, NEW_PASS)
    assert count == 0

"""Tests for envault.env_watch module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.env_watch import (
    get_last_seen_fingerprint,
    has_changed,
    update_fingerprint,
    watch_once,
    _vault_fingerprint,
)


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    vault = tmp_path / "vault.json"
    vault.write_text(json.dumps({"entries": [], "version": 1}))
    return tmp_path


def test_fingerprint_returns_string(vault_dir: Path) -> None:
    fp = _vault_fingerprint(vault_dir / "vault.json")
    assert isinstance(fp, str)
    assert len(fp) == 32  # MD5 hex


def test_fingerprint_missing_file_returns_empty(tmp_path: Path) -> None:
    fp = _vault_fingerprint(tmp_path / "nonexistent.json")
    assert fp == ""


def test_get_last_seen_returns_none_when_absent(vault_dir: Path) -> None:
    assert get_last_seen_fingerprint(vault_dir) is None


def test_update_fingerprint_records_value(vault_dir: Path) -> None:
    fp = update_fingerprint(vault_dir)
    assert fp == get_last_seen_fingerprint(vault_dir)


def test_has_changed_true_before_first_mark(vault_dir: Path) -> None:
    assert has_changed(vault_dir) is True


def test_has_changed_false_after_mark(vault_dir: Path) -> None:
    update_fingerprint(vault_dir)
    assert has_changed(vault_dir) is False


def test_has_changed_true_after_modification(vault_dir: Path) -> None:
    update_fingerprint(vault_dir)
    vault = vault_dir / "vault.json"
    vault.write_text(json.dumps({"entries": ["new"], "version": 2}))
    assert has_changed(vault_dir) is True


def test_watch_once_calls_callback_on_change(vault_dir: Path) -> None:
    called = []
    watch_once(vault_dir, lambda p: called.append(p))
    assert len(called) == 1


def test_watch_once_no_callback_when_unchanged(vault_dir: Path) -> None:
    update_fingerprint(vault_dir)
    called = []
    changed = watch_once(vault_dir, lambda p: called.append(p))
    assert not changed
    assert called == []


def test_watch_once_updates_baseline(vault_dir: Path) -> None:
    vault = vault_dir / "vault.json"
    watch_once(vault_dir, lambda p: None)
    fp_after = get_last_seen_fingerprint(vault_dir)
    expected = _vault_fingerprint(vault)
    assert fp_after == expected

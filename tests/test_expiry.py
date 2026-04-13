"""Tests for envault.expiry module."""

import pytest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from envault.expiry import (
    set_expiry,
    get_expiry,
    remove_expiry,
    is_expired,
    list_expired,
    list_all_expiry,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_expiry_returns_iso_string(vault_dir):
    iso = set_expiry(vault_dir, "DB_PASS", 30)
    assert isinstance(iso, str)
    dt = datetime.fromisoformat(iso)
    assert dt > datetime.now(timezone.utc)


def test_get_expiry_returns_none_when_not_set(vault_dir):
    assert get_expiry(vault_dir, "MISSING") is None


def test_get_expiry_returns_set_value(vault_dir):
    iso = set_expiry(vault_dir, "API_KEY", 10)
    assert get_expiry(vault_dir, "API_KEY") == iso


def test_is_expired_false_for_future(vault_dir):
    set_expiry(vault_dir, "TOKEN", 5)
    assert is_expired(vault_dir, "TOKEN") is False


def test_is_expired_true_for_past(vault_dir, tmp_path):
    import json
    expiry_path = tmp_path / "expiry.json"
    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    expiry_path.write_text(json.dumps({"OLD_KEY": past}))
    assert is_expired(vault_dir=str(tmp_path), label="OLD_KEY") is True


def test_is_expired_false_when_no_expiry(vault_dir):
    assert is_expired(vault_dir, "NO_EXPIRY") is False


def test_remove_expiry_returns_true(vault_dir):
    set_expiry(vault_dir, "SECRET", 7)
    result = remove_expiry(vault_dir, "SECRET")
    assert result is True
    assert get_expiry(vault_dir, "SECRET") is None


def test_remove_expiry_returns_false_when_missing(vault_dir):
    assert remove_expiry(vault_dir, "GHOST") is False


def test_list_expired_returns_only_past(vault_dir, tmp_path):
    import json
    past = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    future = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    data = {"OLD": past, "NEW": future}
    (tmp_path / "expiry.json").write_text(json.dumps(data))
    expired = list_expired(str(tmp_path))
    assert "OLD" in expired
    assert "NEW" not in expired


def test_list_all_expiry_returns_dict(vault_dir):
    set_expiry(vault_dir, "A", 1)
    set_expiry(vault_dir, "B", 2)
    all_exp = list_all_expiry(vault_dir)
    assert "A" in all_exp
    assert "B" in all_exp


def test_list_all_expiry_empty(vault_dir):
    assert list_all_expiry(vault_dir) == {}

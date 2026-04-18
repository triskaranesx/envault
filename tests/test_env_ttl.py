"""Tests for envault.env_ttl module."""
import pytest
from pathlib import Path
from envault.env_ttl import (
    set_ttl, get_ttl, remove_ttl, is_expired, list_expired, list_ttls
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_ttl_returns_iso_string(vault_dir):
    iso = set_ttl(vault_dir, "DB_PASS", 3600)
    assert isinstance(iso, str)
    assert "T" in iso  # ISO format


def test_get_ttl_returns_none_when_absent(vault_dir):
    assert get_ttl(vault_dir, "MISSING") is None


def test_get_ttl_returns_record(vault_dir):
    set_ttl(vault_dir, "API_KEY", 60)
    record = get_ttl(vault_dir, "API_KEY")
    assert record is not None
    assert record["seconds"] == 60
    assert "expires_at" in record


def test_is_expired_false_for_future(vault_dir):
    set_ttl(vault_dir, "FRESH", 9999)
    assert is_expired(vault_dir, "FRESH") is False


def test_is_expired_true_for_past(vault_dir):
    set_ttl(vault_dir, "OLD", 1)
    # Manually backdate the expiry
    import json
    from pathlib import Path
    p = Path(vault_dir) / "ttl.json"
    data = json.loads(p.read_text())
    data["OLD"]["expires_at"] = "2000-01-01T00:00:00+00:00"
    p.write_text(json.dumps(data))
    assert is_expired(vault_dir, "OLD") is True


def test_is_expired_returns_false_when_no_ttl(vault_dir):
    assert is_expired(vault_dir, "NONE") is False


def test_remove_ttl_returns_true_when_exists(vault_dir):
    set_ttl(vault_dir, "X", 100)
    assert remove_ttl(vault_dir, "X") is True
    assert get_ttl(vault_dir, "X") is None


def test_remove_ttl_returns_false_when_absent(vault_dir):
    assert remove_ttl(vault_dir, "GHOST") is False


def test_list_ttls_returns_all(vault_dir):
    set_ttl(vault_dir, "A", 10)
    set_ttl(vault_dir, "B", 20)
    result = list_ttls(vault_dir)
    assert "A" in result
    assert "B" in result


def test_list_expired_returns_only_expired(vault_dir):
    import json
    from pathlib import Path
    set_ttl(vault_dir, "LIVE", 9999)
    set_ttl(vault_dir, "DEAD", 1)
    p = Path(vault_dir) / "ttl.json"
    data = json.loads(p.read_text())
    data["DEAD"]["expires_at"] = "2000-01-01T00:00:00+00:00"
    p.write_text(json.dumps(data))
    expired = list_expired(vault_dir)
    assert "DEAD" in expired
    assert "LIVE" not in expired


def test_set_ttl_empty_label_raises(vault_dir):
    with pytest.raises(ValueError):
        set_ttl(vault_dir, "", 60)


def test_set_ttl_zero_seconds_raises(vault_dir):
    with pytest.raises(ValueError):
        set_ttl(vault_dir, "X", 0)

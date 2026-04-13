"""Tests for envault.audit module."""

import os
import pytest
from envault.audit import (
    record_access,
    get_audit_log,
    clear_audit_log,
    AUDIT_FILE,
)


@pytest.fixture
def tmp_vault(tmp_path):
    vault_file = tmp_path / "test.envault"
    vault_file.write_text("{}")
    return str(vault_file)


def test_empty_audit_returns_list(tmp_vault):
    log = get_audit_log(tmp_vault)
    assert log == []


def test_record_access_creates_entry(tmp_vault):
    entry = record_access(tmp_vault, action="read", label="DB_URL")
    assert entry["action"] == "read"
    assert entry["label"] == "DB_URL"


def test_record_access_includes_timestamp(tmp_vault):
    entry = record_access(tmp_vault, action="write", label="API_KEY")
    assert "timestamp" in entry
    assert "T" in entry["timestamp"]  # ISO 8601 format


def test_record_access_stores_actor(tmp_vault):
    record_access(tmp_vault, action="read", label="SECRET", actor="alice")
    log = get_audit_log(tmp_vault)
    assert log[0]["actor"] == "alice"


def test_record_access_stores_note(tmp_vault):
    record_access(tmp_vault, action="export", label="TOKEN", note="shared with bob")
    log = get_audit_log(tmp_vault)
    assert log[0]["note"] == "shared with bob"


def test_multiple_entries_accumulate(tmp_vault):
    record_access(tmp_vault, action="read", label="A")
    record_access(tmp_vault, action="write", label="B")
    record_access(tmp_vault, action="delete", label="C")
    log = get_audit_log(tmp_vault)
    assert len(log) == 3


def test_filter_by_label(tmp_vault):
    record_access(tmp_vault, action="read", label="DB_URL")
    record_access(tmp_vault, action="write", label="API_KEY")
    log = get_audit_log(tmp_vault, label="DB_URL")
    assert all(e["label"] == "DB_URL" for e in log)
    assert len(log) == 1


def test_filter_by_action(tmp_vault):
    record_access(tmp_vault, action="read", label="X")
    record_access(tmp_vault, action="write", label="Y")
    record_access(tmp_vault, action="read", label="Z")
    log = get_audit_log(tmp_vault, action="read")
    assert len(log) == 2
    assert all(e["action"] == "read" for e in log)


def test_clear_audit_log(tmp_vault):
    record_access(tmp_vault, action="read", label="DB_URL")
    clear_audit_log(tmp_vault)
    assert get_audit_log(tmp_vault) == []


def test_audit_file_created_on_record(tmp_vault):
    audit_path = os.path.join(os.path.dirname(tmp_vault), AUDIT_FILE)
    assert not os.path.exists(audit_path)
    record_access(tmp_vault, action="read", label="KEY")
    assert os.path.exists(audit_path)

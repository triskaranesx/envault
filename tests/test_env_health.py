"""Tests for envault.env_health module."""

import json
import pytest
from pathlib import Path

from envault.vault import init_vault, add_entry
from envault.expiry import set_expiry
from envault.env_health import check_vault_health, HealthReport


PASSWORD = "healthpass"


@pytest.fixture
def vault_dir(tmp_path):
    d = str(tmp_path)
    init_vault(d, PASSWORD)
    return d


def test_missing_vault_returns_error(tmp_path):
    report = check_vault_health(str(tmp_path))
    assert report.has_errors
    assert any("vault.json not found" in i.message for i in report.issues)


def test_corrupt_vault_returns_error(tmp_path):
    vault_file = tmp_path / "vault.json"
    vault_file.write_text("not valid json")
    report = check_vault_health(str(tmp_path))
    assert report.has_errors
    assert any("corrupt" in i.message for i in report.issues)


def test_empty_vault_returns_info(vault_dir):
    report = check_vault_health(vault_dir)
    assert not report.has_errors
    assert any(i.level == "info" for i in report.issues)


def test_healthy_vault_no_errors(vault_dir):
    add_entry(vault_dir, "DB_URL", "postgres://localhost", PASSWORD)
    add_entry(vault_dir, "API_KEY", "secret123", PASSWORD)
    report = check_vault_health(vault_dir)
    assert not report.has_errors
    assert not report.has_warnings


def test_expired_entry_triggers_warning(vault_dir):
    add_entry(vault_dir, "OLD_KEY", "value", PASSWORD)
    # Set expiry to a past date
    set_expiry(vault_dir, "OLD_KEY", "2000-01-01")
    report = check_vault_health(vault_dir)
    assert report.has_warnings
    assert any("OLD_KEY" == i.label and "expired" in i.message for i in report.issues)


def test_non_expired_entry_no_warning(vault_dir):
    add_entry(vault_dir, "FRESH_KEY", "value", PASSWORD)
    set_expiry(vault_dir, "FRESH_KEY", "2099-12-31")
    report = check_vault_health(vault_dir)
    assert not any(i.label == "FRESH_KEY" and "expired" in i.message for i in report.issues)


def test_summary_format(vault_dir):
    add_entry(vault_dir, "STALE", "val", PASSWORD)
    set_expiry(vault_dir, "STALE", "2000-01-01")
    report = check_vault_health(vault_dir)
    summary = report.summary()
    assert "error" in summary
    assert "warning" in summary


def test_health_report_is_dataclass(vault_dir):
    report = check_vault_health(vault_dir)
    assert isinstance(report, HealthReport)
    assert isinstance(report.issues, list)

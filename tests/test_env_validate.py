"""Tests for envault.env_validate."""

from __future__ import annotations

import pytest

from envault.env_validate import (
    ValidationIssue,
    ValidationResult,
    validate_entries,
    _check_label_format,
    _check_empty_value,
    _check_placeholder_value,
    _check_url_scheme,
)


# ---------------------------------------------------------------------------
# Unit-level rule checks
# ---------------------------------------------------------------------------

def test_check_label_format_valid():
    assert _check_label_format("DATABASE_URL") is None


def test_check_label_format_lowercase_triggers_warning():
    issue = _check_label_format("database_url")
    assert issue is not None
    assert issue.severity == "warning"
    assert issue.rule == "label_format"


def test_check_label_format_special_chars_triggers_warning():
    issue = _check_label_format("MY-KEY")
    assert issue is not None


def test_check_empty_value_empty_string():
    issue = _check_empty_value("TOKEN", "")
    assert issue is not None
    assert issue.severity == "error"
    assert issue.rule == "empty_value"


def test_check_empty_value_whitespace_only():
    issue = _check_empty_value("TOKEN", "   ")
    assert issue is not None
    assert issue.severity == "error"


def test_check_empty_value_non_empty():
    assert _check_empty_value("TOKEN", "abc123") is None


def test_check_placeholder_changeme():
    issue = _check_placeholder_value("SECRET", "CHANGEME")
    assert issue is not None
    assert issue.rule == "placeholder_value"
    assert issue.severity == "warning"


def test_check_placeholder_angle_brackets():
    issue = _check_placeholder_value("SECRET", "<your-secret>")
    assert issue is not None


def test_check_placeholder_real_value():
    assert _check_placeholder_value("SECRET", "s3cr3t!xyz") is None


def test_check_url_scheme_missing_http():
    issue = _check_url_scheme("DATABASE_URL", "postgres://localhost/db")
    assert issue is not None
    assert issue.rule == "url_scheme"
    assert issue.severity == "warning"


def test_check_url_scheme_valid_https():
    assert _check_url_scheme("API_ENDPOINT", "https://api.example.com") is None


def test_check_url_scheme_non_url_label():
    # label doesn't contain 'url'/'uri'/'endpoint' — should not trigger
    assert _check_url_scheme("SECRET_KEY", "notaurl") is None


# ---------------------------------------------------------------------------
# validate_entries integration
# ---------------------------------------------------------------------------

def test_validate_entries_all_clean():
    entries = [{"label": "API_KEY", "value": "abc123"}, {"label": "DB_HOST", "value": "localhost"}]
    result = validate_entries(entries)
    assert result.valid
    assert result.issues == []


def test_validate_entries_collects_multiple_issues():
    entries = [
        {"label": "bad-label", "value": ""},
        {"label": "OK_LABEL", "value": "CHANGEME"},
    ]
    result = validate_entries(entries)
    assert len(result.issues) >= 2


def test_validate_entries_valid_false_on_error():
    entries = [{"label": "X", "value": ""}]
    result = validate_entries(entries)
    assert not result.valid


def test_validate_entries_warnings_do_not_make_invalid():
    entries = [{"label": "lowercase", "value": "real_value"}]
    result = validate_entries(entries)
    # label format warning but no errors → still valid
    assert result.valid
    assert len(result.warnings) >= 1


def test_validation_result_errors_and_warnings_split():
    issues = [
        ValidationIssue(label="A", rule="r1", message="m1", severity="error"),
        ValidationIssue(label="B", rule="r2", message="m2", severity="warning"),
    ]
    result = ValidationResult(issues=issues)
    assert len(result.errors) == 1
    assert len(result.warnings) == 1

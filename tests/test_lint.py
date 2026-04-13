"""Tests for envault.lint module."""

import pytest

from envault.vault import init_vault, add_entry
from envault.lint import lint_vault, _check_label_format, _check_empty_value, _check_whitespace, _check_placeholder


@pytest.fixture
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


# --- Unit tests for individual checks ---

def test_check_label_format_valid():
    assert _check_label_format("MY_VAR") == []


def test_check_label_format_lowercase_warning():
    issues = _check_label_format("my_var")
    assert any("uppercase" in i for i in issues)


def test_check_label_format_special_chars():
    issues = _check_label_format("MY VAR!")
    assert any("characters" in i for i in issues)


def test_check_empty_value_empty():
    issues = _check_empty_value("KEY", "")
    assert any("empty" in i for i in issues)


def test_check_empty_value_nonempty():
    assert _check_empty_value("KEY", "hello") == []


def test_check_whitespace_leading():
    issues = _check_whitespace("KEY", "  value")
    assert any("whitespace" in i for i in issues)


def test_check_whitespace_trailing():
    issues = _check_whitespace("KEY", "value  ")
    assert any("whitespace" in i for i in issues)


def test_check_whitespace_clean():
    assert _check_whitespace("KEY", "value") == []


def test_check_placeholder_detected():
    issues = _check_placeholder("KEY", "CHANGEME")
    assert any("placeholder" in i for i in issues)


def test_check_placeholder_angle_brackets():
    issues = _check_placeholder("KEY", "<my-value>")
    assert any("placeholder" in i for i in issues)


def test_check_placeholder_real_value():
    assert _check_placeholder("KEY", "s3cr3t!") == []


# --- Integration tests ---

def test_lint_clean_vault(vault_dir):
    add_entry(vault_dir, "DB_HOST", "localhost", "password")
    result = lint_vault(vault_dir, "password")
    assert result["checked"] == 1
    assert result["issues"] == []


def test_lint_detects_lowercase_label(vault_dir):
    add_entry(vault_dir, "db_host", "localhost", "password")
    result = lint_vault(vault_dir, "password")
    assert any("uppercase" in i for i in result["issues"])


def test_lint_detects_placeholder_value(vault_dir):
    add_entry(vault_dir, "API_KEY", "CHANGEME", "password")
    result = lint_vault(vault_dir, "password")
    assert any("placeholder" in i for i in result["issues"])


def test_lint_empty_vault_returns_zero(vault_dir):
    result = lint_vault(vault_dir, "password")
    assert result["checked"] == 0
    assert result["issues"] == []


def test_lint_filter_by_labels(vault_dir):
    add_entry(vault_dir, "DB_HOST", "localhost", "password")
    add_entry(vault_dir, "api_key", "secret", "password")
    result = lint_vault(vault_dir, "password", labels=["DB_HOST"])
    assert result["checked"] == 1

"""Tests for envault.env_schema — schema definition and validation."""

import pytest
from pathlib import Path

from envault.env_schema import (
    load_schema,
    save_schema,
    set_field,
    remove_field,
    validate_against_schema,
)


@pytest.fixture
def vault_dir(tmp_path: Path) -> str:
    return str(tmp_path)


def test_load_schema_returns_empty_when_absent(vault_dir):
    assert load_schema(vault_dir) == {}


def test_set_field_creates_entry(vault_dir):
    set_field(vault_dir, "DATABASE_URL", required=True, field_type="url")
    schema = load_schema(vault_dir)
    assert "DATABASE_URL" in schema
    assert schema["DATABASE_URL"]["required"] is True
    assert schema["DATABASE_URL"]["type"] == "url"


def test_set_field_defaults(vault_dir):
    set_field(vault_dir, "APP_NAME")
    schema = load_schema(vault_dir)
    assert schema["APP_NAME"]["required"] is False
    assert schema["APP_NAME"]["type"] == "string"


def test_set_field_invalid_type_raises(vault_dir):
    with pytest.raises(ValueError, match="Invalid type"):
        set_field(vault_dir, "SOME_FIELD", field_type="float")


def test_set_field_overwrites_existing(vault_dir):
    set_field(vault_dir, "PORT", field_type="string")
    set_field(vault_dir, "PORT", field_type="integer", required=True)
    schema = load_schema(vault_dir)
    assert schema["PORT"]["type"] == "integer"
    assert schema["PORT"]["required"] is True


def test_remove_field_returns_true_when_exists(vault_dir):
    set_field(vault_dir, "SECRET_KEY")
    result = remove_field(vault_dir, "SECRET_KEY")
    assert result is True
    assert "SECRET_KEY" not in load_schema(vault_dir)


def test_remove_field_returns_false_when_absent(vault_dir):
    result = remove_field(vault_dir, "NONEXISTENT")
    assert result is False


def test_validate_missing_required_field(vault_dir):
    set_field(vault_dir, "DATABASE_URL", required=True, field_type="url")
    issues = validate_against_schema(vault_dir, {})
    assert any("DATABASE_URL" in i and "missing" in i for i in issues)


def test_validate_optional_missing_field_no_issue(vault_dir):
    set_field(vault_dir, "OPTIONAL_KEY", required=False)
    issues = validate_against_schema(vault_dir, {})
    assert issues == []


def test_validate_integer_type_valid(vault_dir):
    set_field(vault_dir, "PORT", field_type="integer")
    issues = validate_against_schema(vault_dir, {"PORT": "8080"})
    assert issues == []


def test_validate_integer_type_invalid(vault_dir):
    set_field(vault_dir, "PORT", field_type="integer")
    issues = validate_against_schema(vault_dir, {"PORT": "not-a-number"})
    assert any("PORT" in i for i in issues)


def test_validate_url_type_valid(vault_dir):
    set_field(vault_dir, "API_URL", field_type="url")
    issues = validate_against_schema(vault_dir, {"API_URL": "https://example.com"})
    assert issues == []


def test_validate_url_type_invalid(vault_dir):
    set_field(vault_dir, "API_URL", field_type="url")
    issues = validate_against_schema(vault_dir, {"API_URL": "not-a-url"})
    assert any("API_URL" in i for i in issues)


def test_validate_boolean_type_valid(vault_dir):
    set_field(vault_dir, "DEBUG", field_type="boolean")
    for val in ["true", "false", "1", "0", "yes", "no", "True", "FALSE"]:
        issues = validate_against_schema(vault_dir, {"DEBUG": val})
        assert issues == [], f"Expected no issues for value {val!r}"


def test_validate_email_type_invalid(vault_dir):
    set_field(vault_dir, "ADMIN_EMAIL", field_type="email")
    issues = validate_against_schema(vault_dir, {"ADMIN_EMAIL": "not-an-email"})
    assert any("ADMIN_EMAIL" in i for i in issues)

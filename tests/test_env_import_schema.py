import pytest
import json
from pathlib import Path
from envault.env_import_schema import validate_against_schema, errors_only, warnings_only


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def _write_schema(vault_dir, schema):
    p = Path(vault_dir) / "schema.json"
    p.write_text(json.dumps(schema))


def test_no_schema_returns_empty(vault_dir):
    result = validate_against_schema(vault_dir, {"FOO": "bar"})
    assert result == []


def test_required_field_missing(vault_dir):
    _write_schema(vault_dir, {"DB_URL": {"required": True, "type": "string"}})
    result = validate_against_schema(vault_dir, {})
    assert len(result) == 1
    assert result[0].label == "DB_URL"
    assert result[0].level == "error"


def test_required_field_present_no_violation(vault_dir):
    _write_schema(vault_dir, {"DB_URL": {"required": True, "type": "string"}})
    result = validate_against_schema(vault_dir, {"DB_URL": "postgres://localhost"})
    assert result == []


def test_integer_type_valid(vault_dir):
    _write_schema(vault_dir, {"PORT": {"type": "integer"}})
    result = validate_against_schema(vault_dir, {"PORT": "8080"})
    assert result == []


def test_integer_type_invalid(vault_dir):
    _write_schema(vault_dir, {"PORT": {"type": "integer"}})
    result = validate_against_schema(vault_dir, {"PORT": "not_a_number"})
    assert len(result) == 1
    assert result[0].label == "PORT"
    assert result[0].level == "error"


def test_boolean_type_valid(vault_dir):
    _write_schema(vault_dir, {"DEBUG": {"type": "boolean"}})
    for val in ("true", "false", "1", "0", "yes", "no"):
        result = validate_against_schema(vault_dir, {"DEBUG": val})
        assert result == [], f"Expected no violations for {val!r}"


def test_boolean_type_invalid(vault_dir):
    _write_schema(vault_dir, {"DEBUG": {"type": "boolean"}})
    result = validate_against_schema(vault_dir, {"DEBUG": "maybe"})
    assert len(result) == 1
    assert result[0].level == "error"


def test_pattern_violation_is_warning(vault_dir):
    _write_schema(vault_dir, {"VERSION": {"type": "string", "pattern": r"\d+\.\d+\.\d+"}})
    result = validate_against_schema(vault_dir, {"VERSION": "not-semver"})
    assert len(result) == 1
    assert result[0].level == "warning"


def test_allowed_values_valid(vault_dir):
    _write_schema(vault_dir, {"ENV": {"allowed": ["dev", "staging", "prod"]}})
    result = validate_against_schema(vault_dir, {"ENV": "prod"})
    assert result == []


def test_allowed_values_invalid(vault_dir):
    _write_schema(vault_dir, {"ENV": {"allowed": ["dev", "staging", "prod"]}})
    result = validate_against_schema(vault_dir, {"ENV": "local"})
    assert len(result) == 1
    assert result[0].level == "error"


def test_errors_only_filters(vault_dir):
    _write_schema(vault_dir, {
        "PORT": {"type": "integer"},
        "VERSION": {"type": "string", "pattern": r"\d+\.\d+\.\d+"}
    })
    result = validate_against_schema(vault_dir, {"PORT": "bad", "VERSION": "bad"})
    assert len(errors_only(result)) == 1
    assert len(warnings_only(result)) == 1

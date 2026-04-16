import json
import pytest
from pathlib import Path
from envault.env_import_schema import validate_against_schema, SchemaViolation


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def _write_schema(vault_dir, schema):
    Path(vault_dir, "schema.json").write_text(json.dumps(schema))


def test_optional_field_absent_no_violation(vault_dir):
    _write_schema(vault_dir, {"OPTIONAL": {"type": "string", "required": False}})
    result = validate_against_schema(vault_dir, {})
    assert result == []


def test_multiple_violations_collected(vault_dir):
    _write_schema(vault_dir, {
        "PORT": {"type": "integer", "required": True},
        "DEBUG": {"type": "boolean", "required": True},
    })
    result = validate_against_schema(vault_dir, {})
    labels = {v.label for v in result}
    assert "PORT" in labels
    assert "DEBUG" in labels


def test_pattern_match_passes(vault_dir):
    _write_schema(vault_dir, {"VER": {"pattern": r"\d+\.\d+\.\d+"}})
    result = validate_against_schema(vault_dir, {"VER": "1.2.3"})
    assert result == []


def test_allowed_list_empty_string_valid(vault_dir):
    _write_schema(vault_dir, {"MODE": {"allowed": ["on", "off", ""]}})
    result = validate_against_schema(vault_dir, {"MODE": ""})
    assert result == []


def test_schema_violation_repr():
    v = SchemaViolation("FOO", "some message", "error")
    r = repr(v)
    assert "FOO" in r
    assert "error" in r
    assert "some message" in r


def test_extra_entries_not_in_schema_ignored(vault_dir):
    _write_schema(vault_dir, {"KNOWN": {"type": "string"}})
    result = validate_against_schema(vault_dir, {"KNOWN": "ok", "UNKNOWN": "value"})
    assert result == []

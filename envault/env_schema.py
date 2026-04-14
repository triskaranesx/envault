"""Schema validation for .env entries — define expected labels, types, and required fields."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

SCHEMA_FILENAME = ".envault_schema.json"

VALID_TYPES = {"string", "integer", "boolean", "url", "email"}

_TYPE_PATTERNS: dict[str, re.Pattern] = {
    "integer": re.compile(r"^-?\d+$"),
    "boolean": re.compile(r"^(true|false|1|0|yes|no)$", re.IGNORECASE),
    "url": re.compile(r"^https?://[^\s]+$"),
    "email": re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$"),
}


def _schema_path(vault_dir: str) -> Path:
    return Path(vault_dir) / SCHEMA_FILENAME


def load_schema(vault_dir: str) -> dict[str, Any]:
    """Load schema from vault directory. Returns empty dict if not found."""
    path = _schema_path(vault_dir)
    if not path.exists():
        return {}
    with path.open("r") as f:
        return json.load(f)


def save_schema(vault_dir: str, schema: dict[str, Any]) -> None:
    """Persist schema to vault directory."""
    path = _schema_path(vault_dir)
    with path.open("w") as f:
        json.dump(schema, f, indent=2)


def set_field(vault_dir: str, label: str, *, required: bool = False,
              field_type: str = "string", description: str = "") -> None:
    """Add or update a schema field definition."""
    if field_type not in VALID_TYPES:
        raise ValueError(f"Invalid type '{field_type}'. Must be one of: {', '.join(sorted(VALID_TYPES))}")
    schema = load_schema(vault_dir)
    schema[label] = {
        "required": required,
        "type": field_type,
        "description": description,
    }
    save_schema(vault_dir, schema)


def remove_field(vault_dir: str, label: str) -> bool:
    """Remove a field from the schema. Returns True if it existed."""
    schema = load_schema(vault_dir)
    if label not in schema:
        return False
    del schema[label]
    save_schema(vault_dir, schema)
    return True


def validate_against_schema(vault_dir: str, entries: dict[str, str]) -> list[str]:
    """Validate a dict of label->value pairs against the schema.
    Returns a list of issue messages (empty means valid)."""
    schema = load_schema(vault_dir)
    issues: list[str] = []

    for label, field in schema.items():
        if field.get("required") and label not in entries:
            issues.append(f"Required field '{label}' is missing.")
            continue
        if label not in entries:
            continue
        value = entries[label]
        ftype = field.get("type", "string")
        pattern = _TYPE_PATTERNS.get(ftype)
        if pattern and not pattern.match(value):
            issues.append(f"Field '{label}' has type '{ftype}' but value does not match: {value!r}")

    return issues

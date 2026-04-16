"""Validate imported .env entries against a defined schema."""
from typing import List, Dict, Any
from envault.env_schema import load_schema


class SchemaViolation:
    def __init__(self, label: str, message: str, level: str = "error"):
        self.label = label
        self.message = message
        self.level = level

    def __repr__(self):
        return f"SchemaViolation({self.level}, {self.label!r}: {self.message})"


def validate_against_schema(vault_dir: str, entries: Dict[str, str]) -> List[SchemaViolation]:
    """Validate a dict of label->value pairs against the vault schema."""
    schema = load_schema(vault_dir)
    violations: List[SchemaViolation] = []

    for label, field in schema.items():
        required = field.get("required", False)
        if required and label not in entries:
            violations.append(SchemaViolation(label, "required field is missing", "error"))
            continue

        if label not in entries:
            continue

        value = entries[label]
        expected_type = field.get("type", "string")

        if expected_type == "integer":
            try:
                int(value)
            except ValueError:
                violations.append(SchemaViolation(label, f"expected integer, got {value!r}", "error"))

        elif expected_type == "boolean":
            if value.lower() not in ("true", "false", "1", "0", "yes", "no"):
                violations.append(SchemaViolation(label, f"expected boolean, got {value!r}", "error"))

        pattern = field.get("pattern")
        if pattern:
            import re
            if not re.fullmatch(pattern, value):
                violations.append(SchemaViolation(label, f"value does not match pattern {pattern!r}", "warning"))

        allowed = field.get("allowed")
        if allowed and value not in allowed:
            violations.append(SchemaViolation(label, f"value {value!r} not in allowed list", "error"))

    return violations


def errors_only(violations: List[SchemaViolation]) -> List[SchemaViolation]:
    return [v for v in violations if v.level == "error"]


def warnings_only(violations: List[SchemaViolation]) -> List[SchemaViolation]:
    return [v for v in violations if v.level == "warning"]

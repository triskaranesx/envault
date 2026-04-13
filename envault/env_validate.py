"""Validation rules for .env entries in the vault."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ValidationIssue:
    label: str
    rule: str
    message: str
    severity: str = "error"  # "error" | "warning"


@dataclass
class ValidationResult:
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)

    @property
    def errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]


_LABEL_RE = re.compile(r'^[A-Z][A-Z0-9_]*$')
_URL_RE = re.compile(r'^https?://', re.IGNORECASE)
_COMMON_PLACEHOLDERS = {"CHANGEME", "TODO", "FIXME", "PLACEHOLDER", "EXAMPLE", "YOUR_", "<", ">"}


def _check_label_format(label: str) -> Optional[ValidationIssue]:
    if not _LABEL_RE.match(label):
        return ValidationIssue(
            label=label,
            rule="label_format",
            message=f"Label '{label}' should be UPPER_SNAKE_CASE.",
            severity="warning",
        )
    return None


def _check_empty_value(label: str, value: str) -> Optional[ValidationIssue]:
    if value.strip() == "":
        return ValidationIssue(
            label=label,
            rule="empty_value",
            message=f"Label '{label}' has an empty value.",
            severity="error",
        )
    return None


def _check_placeholder_value(label: str, value: str) -> Optional[ValidationIssue]:
    upper = value.upper()
    for token in _COMMON_PLACEHOLDERS:
        if token in upper:
            return ValidationIssue(
                label=label,
                rule="placeholder_value",
                message=f"Label '{label}' looks like a placeholder: '{value}'.",
                severity="warning",
            )
    return None


def _check_url_scheme(label: str, value: str) -> Optional[ValidationIssue]:
    lower_label = label.lower()
    if ("url" in lower_label or "uri" in lower_label or "endpoint" in lower_label):
        if value and not _URL_RE.match(value):
            return ValidationIssue(
                label=label,
                rule="url_scheme",
                message=f"Label '{label}' looks like a URL but value doesn't start with http(s)://.",
                severity="warning",
            )
    return None


def validate_entries(entries: list[dict]) -> ValidationResult:
    """Run all validation rules against a list of decrypted entry dicts.

    Each entry dict must have keys: 'label' and 'value'.
    """
    result = ValidationResult()
    checkers = [
        _check_label_format,
        lambda l, v: _check_empty_value(l, v),
        lambda l, v: _check_placeholder_value(l, v),
        lambda l, v: _check_url_scheme(l, v),
    ]
    for entry in entries:
        label = entry.get("label", "")
        value = entry.get("value", "")
        for checker in checkers:
            try:
                issue = checker(label, value)
            except TypeError:
                issue = checker(label)
            if issue:
                result.issues.append(issue)
    return result

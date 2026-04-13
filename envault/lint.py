"""Lint/validate .env entries in the vault for common issues."""

from __future__ import annotations

from typing import Any

from envault.vault import list_entries, get_entry
from envault.crypto import decrypt

# Rules: each returns (passed: bool, message: str)


def _check_empty_value(label: str, value: str) -> list[str]:
    issues = []
    if value.strip() == "":
        issues.append(f"[{label}] Value is empty.")
    return issues


def _check_whitespace(label: str, value: str) -> list[str]:
    issues = []
    if value != value.strip():
        issues.append(f"[{label}] Value has leading or trailing whitespace.")
    return issues


def _check_label_format(label: str) -> list[str]:
    issues = []
    if not label.replace("_", "").replace("-", "").isalnum():
        issues.append(
            f"[{label}] Label contains characters other than alphanumeric, '_', or '-'."
        )
    if label != label.upper():
        issues.append(f"[{label}] Label is not uppercase (convention).")
    return issues


def _check_placeholder(label: str, value: str) -> list[str]:
    issues = []
    placeholders = {"CHANGEME", "TODO", "FIXME", "PLACEHOLDER", "XXX", "<VALUE>"}
    if value.upper() in placeholders or value.startswith("<") and value.endswith(">"):
        issues.append(f"[{label}] Value looks like a placeholder: '{value}'.")
    return issues


def lint_vault(vault_path: str, password: str, labels: list[str] | None = None) -> dict[str, Any]:
    """Run lint checks on vault entries.

    Returns a dict with 'issues' (list of str) and 'checked' (int).
    Raises ValueError if no entries exist.
    """
    entries = list_entries(vault_path)
    if labels:
        entries = [e for e in entries if e["label"] in labels]

    if not entries:
        return {"issues": [], "checked": 0}

    all_issues: list[str] = []

    for entry in entries:
        label = entry["label"]
        encrypted = entry["value"]
        try:
            value = decrypt(encrypted, password)
        except Exception:
            all_issues.append(f"[{label}] Could not decrypt value (wrong password?).")
            continue

        all_issues.extend(_check_label_format(label))
        all_issues.extend(_check_empty_value(label, value))
        all_issues.extend(_check_whitespace(label, value))
        all_issues.extend(_check_placeholder(label, value))

    return {"issues": all_issues, "checked": len(entries)}

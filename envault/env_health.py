"""Health check module for envault vaults."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envault.vault import _load_vault_raw
from envault.expiry import get_expiry, is_expired
from envault.env_schema import load_schema


@dataclass
class HealthIssue:
    level: str  # "error" | "warning" | "info"
    label: Optional[str]
    message: str


@dataclass
class HealthReport:
    issues: List[HealthIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.level == "error" for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.level == "warning" for i in self.issues)

    def summary(self) -> str:
        errors = sum(1 for i in self.issues if i.level == "error")
        warnings = sum(1 for i in self.issues if i.level == "warning")
        return f"{errors} error(s), {warnings} warning(s)"


def check_vault_health(vault_dir: str) -> HealthReport:
    """Run all health checks against a vault directory."""
    report = HealthReport()
    path = Path(vault_dir)

    vault_file = path / "vault.json"
    if not vault_file.exists():
        report.issues.append(HealthIssue("error", None, "vault.json not found — run 'envault init' first"))
        return report

    try:
        vault = _load_vault_raw(vault_dir)
    except (json.JSONDecodeError, KeyError) as exc:
        report.issues.append(HealthIssue("error", None, f"vault.json is corrupt: {exc}"))
        return report

    entries = vault.get("entries", [])
    if not entries:
        report.issues.append(HealthIssue("info", None, "Vault is empty"))
        return report

    schema = load_schema(vault_dir)

    for entry in entries:
        label = entry.get("label", "<unknown>")

        # Check for missing ciphertext
        if not entry.get("ciphertext"):
            report.issues.append(HealthIssue("error", label, "Entry has no ciphertext"))

        # Check expiry
        expiry = get_expiry(vault_dir, label)
        if expiry and is_expired(vault_dir, label):
            report.issues.append(HealthIssue("warning", label, f"Entry expired on {expiry}"))

        # Check schema required fields
        field_def = schema.get(label)
        if field_def and field_def.get("required") and not entry.get("ciphertext"):
            report.issues.append(HealthIssue("error", label, "Required schema field has no value"))

    return report

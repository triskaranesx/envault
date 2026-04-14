"""Generate human-readable diff reports between two vault snapshots or states."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envault.crypto import decrypt


@dataclass
class DiffEntry:
    label: str
    status: str  # 'added' | 'removed' | 'changed' | 'unchanged'
    old_value: Optional[str] = None
    new_value: Optional[str] = None


@dataclass
class DiffReport:
    added: List[DiffEntry] = field(default_factory=list)
    removed: List[DiffEntry] = field(default_factory=list)
    changed: List[DiffEntry] = field(default_factory=list)
    unchanged: List[DiffEntry] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        parts = []
        if self.added:
            parts.append(f"+{len(self.added)} added")
        if self.removed:
            parts.append(f"-{len(self.removed)} removed")
        if self.changed:
            parts.append(f"~{len(self.changed)} changed")
        if not parts:
            return "No changes."
        return ", ".join(parts)


def _decrypt_entries(entries: List[dict], password: str) -> Dict[str, str]:
    """Decrypt a list of vault entries into {label: value} mapping."""
    result = {}
    for entry in entries:
        label = entry.get("label", "")
        try:
            value = decrypt(entry["ciphertext"], password)
        except Exception:
            value = "<decryption-failed>"
        result[label] = value
    return result


def build_diff_report(
    base_entries: List[dict],
    other_entries: List[dict],
    password: str,
    include_unchanged: bool = False,
) -> DiffReport:
    """Compare two lists of vault entries and return a DiffReport."""
    base = _decrypt_entries(base_entries, password)
    other = _decrypt_entries(other_entries, password)

    all_labels = set(base) | set(other)
    report = DiffReport()

    for label in sorted(all_labels):
        in_base = label in base
        in_other = label in other

        if in_base and not in_other:
            report.removed.append(DiffEntry(label, "removed", old_value=base[label]))
        elif in_other and not in_base:
            report.added.append(DiffEntry(label, "added", new_value=other[label]))
        elif base[label] != other[label]:
            report.changed.append(
                DiffEntry(label, "changed", old_value=base[label], new_value=other[label])
            )
        elif include_unchanged:
            report.unchanged.append(DiffEntry(label, "unchanged", old_value=base[label]))

    return report


def format_report(report: DiffReport, show_values: bool = False) -> str:
    """Render a DiffReport as a printable string."""
    lines = []
    for entry in report.added:
        val = f" = {entry.new_value}" if show_values else ""
        lines.append(f"  [+] {entry.label}{val}")
    for entry in report.removed:
        val = f" = {entry.old_value}" if show_values else ""
        lines.append(f"  [-] {entry.label}{val}")
    for entry in report.changed:
        if show_values:
            lines.append(f"  [~] {entry.label}: {entry.old_value!r} -> {entry.new_value!r}")
        else:
            lines.append(f"  [~] {entry.label}")
    for entry in report.unchanged:
        lines.append(f"  [ ] {entry.label}")
    if not lines:
        return "No changes."
    return "\n".join(lines)

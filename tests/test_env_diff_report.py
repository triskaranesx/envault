"""Tests for envault.env_diff_report."""

import pytest

from envault.crypto import encrypt
from envault.env_diff_report import (
    DiffReport,
    build_diff_report,
    format_report,
)

PASSWORD = "test-password"


def _make_entry(label: str, value: str, password: str = PASSWORD) -> dict:
    return {"label": label, "ciphertext": encrypt(value, password)}


# ---------------------------------------------------------------------------
# build_diff_report
# ---------------------------------------------------------------------------

def test_no_changes_returns_empty_report():
    entries = [_make_entry("DB_HOST", "localhost")]
    report = build_diff_report(entries, entries, PASSWORD)
    assert not report.has_changes
    assert report.added == []
    assert report.removed == []
    assert report.changed == []


def test_added_label_detected():
    base = [_make_entry("DB_HOST", "localhost")]
    other = [
        _make_entry("DB_HOST", "localhost"),
        _make_entry("DB_PORT", "5432"),
    ]
    report = build_diff_report(base, other, PASSWORD)
    assert len(report.added) == 1
    assert report.added[0].label == "DB_PORT"
    assert report.added[0].new_value == "5432"


def test_removed_label_detected():
    base = [
        _make_entry("DB_HOST", "localhost"),
        _make_entry("DB_PORT", "5432"),
    ]
    other = [_make_entry("DB_HOST", "localhost")]
    report = build_diff_report(base, other, PASSWORD)
    assert len(report.removed) == 1
    assert report.removed[0].label == "DB_PORT"
    assert report.removed[0].old_value == "5432"


def test_changed_label_detected():
    base = [_make_entry("API_KEY", "old-key")]
    other = [_make_entry("API_KEY", "new-key")]
    report = build_diff_report(base, other, PASSWORD)
    assert len(report.changed) == 1
    entry = report.changed[0]
    assert entry.label == "API_KEY"
    assert entry.old_value == "old-key"
    assert entry.new_value == "new-key"


def test_include_unchanged_flag():
    entries = [_make_entry("SAME", "value")]
    report = build_diff_report(entries, entries, PASSWORD, include_unchanged=True)
    assert len(report.unchanged) == 1
    assert report.unchanged[0].label == "SAME"


def test_has_changes_true_when_diff():
    base = [_make_entry("X", "1")]
    other = [_make_entry("X", "2")]
    report = build_diff_report(base, other, PASSWORD)
    assert report.has_changes


def test_summary_no_changes():
    entries = [_make_entry("K", "v")]
    report = build_diff_report(entries, entries, PASSWORD)
    assert report.summary() == "No changes."


def test_summary_with_changes():
    base = [_make_entry("A", "1"), _make_entry("B", "2")]
    other = [_make_entry("A", "updated"), _make_entry("C", "3")]
    report = build_diff_report(base, other, PASSWORD)
    summary = report.summary()
    assert "+1 added" in summary
    assert "-1 removed" in summary
    assert "~1 changed" in summary


# ---------------------------------------------------------------------------
# format_report
# ---------------------------------------------------------------------------

def test_format_report_empty():
    report = DiffReport()
    assert format_report(report) == "No changes."


def test_format_report_shows_labels():
    base = [_make_entry("OLD", "x")]
    other = [_make_entry("NEW", "y")]
    report = build_diff_report(base, other, PASSWORD)
    output = format_report(report)
    assert "[+] NEW" in output
    assert "[-] OLD" in output


def test_format_report_show_values():
    base = [_make_entry("KEY", "before")]
    other = [_make_entry("KEY", "after")]
    report = build_diff_report(base, other, PASSWORD)
    output = format_report(report, show_values=True)
    assert "before" in output
    assert "after" in output

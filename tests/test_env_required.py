"""Tests for envault.env_required."""

from __future__ import annotations

import pytest

from envault.env_required import (
    RequiredError,
    check_required,
    is_required,
    list_required,
    mark_required,
    unmark_required,
)


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_list_required_empty(vault_dir):
    assert list_required(vault_dir) == []


def test_mark_required_creates_entry(vault_dir):
    mark_required(vault_dir, "DATABASE_URL")
    assert "DATABASE_URL" in list_required(vault_dir)


def test_mark_required_no_duplicates(vault_dir):
    mark_required(vault_dir, "API_KEY")
    mark_required(vault_dir, "API_KEY")
    assert list_required(vault_dir).count("API_KEY") == 1


def test_mark_required_multiple_labels(vault_dir):
    mark_required(vault_dir, "A")
    mark_required(vault_dir, "B")
    required = list_required(vault_dir)
    assert "A" in required
    assert "B" in required


def test_is_required_false_when_absent(vault_dir):
    assert is_required(vault_dir, "MISSING") is False


def test_is_required_true_after_mark(vault_dir):
    mark_required(vault_dir, "SECRET")
    assert is_required(vault_dir, "SECRET") is True


def test_unmark_required_returns_true_when_present(vault_dir):
    mark_required(vault_dir, "TOKEN")
    result = unmark_required(vault_dir, "TOKEN")
    assert result is True
    assert is_required(vault_dir, "TOKEN") is False


def test_unmark_required_returns_false_when_absent(vault_dir):
    result = unmark_required(vault_dir, "GHOST")
    assert result is False


def test_unmark_does_not_affect_others(vault_dir):
    mark_required(vault_dir, "A")
    mark_required(vault_dir, "B")
    unmark_required(vault_dir, "A")
    assert is_required(vault_dir, "B") is True


def test_mark_required_empty_label_raises(vault_dir):
    with pytest.raises(RequiredError):
        mark_required(vault_dir, "")


def test_mark_required_whitespace_label_raises(vault_dir):
    with pytest.raises(RequiredError):
        mark_required(vault_dir, "   ")


def test_check_required_all_present(vault_dir):
    mark_required(vault_dir, "A")
    mark_required(vault_dir, "B")
    missing = check_required(vault_dir, ["A", "B", "C"])
    assert missing == []


def test_check_required_detects_missing(vault_dir):
    mark_required(vault_dir, "A")
    mark_required(vault_dir, "B")
    missing = check_required(vault_dir, ["A"])
    assert missing == ["B"]


def test_check_required_empty_vault_no_missing(vault_dir):
    missing = check_required(vault_dir, [])
    assert missing == []


def test_list_required_sorted(vault_dir):
    mark_required(vault_dir, "Z")
    mark_required(vault_dir, "A")
    mark_required(vault_dir, "M")
    assert list_required(vault_dir) == ["A", "M", "Z"]

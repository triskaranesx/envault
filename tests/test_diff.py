"""Tests for envault.diff module."""

from __future__ import annotations

import json
import os
import pytest

from envault.crypto import encrypt
from envault.diff import diff_versions, diff_labels

PASSWORD = "test-pass"


@pytest.fixture()
def vault_dir(tmp_path: "pathlib.Path") -> str:
    """Create a minimal vault with two versions of a label."""
    vault_path = str(tmp_path)
    entries = [
        {
            "label": "DB_URL",
            "version": 1,
            "value": encrypt("postgres://localhost/db1", PASSWORD),
        },
        {
            "label": "DB_URL",
            "version": 2,
            "value": encrypt("postgres://localhost/db2", PASSWORD),
        },
        {
            "label": "API_KEY",
            "version": 1,
            "value": encrypt("key-abc", PASSWORD),
        },
    ]
    vault_file = os.path.join(vault_path, "vault.json")
    with open(vault_file, "w") as fh:
        json.dump({"version": 1, "entries": entries}, fh)
    return vault_path


def test_diff_versions_changed(vault_dir: str) -> None:
    result = diff_versions(vault_dir, "DB_URL", PASSWORD, 1, 2)
    assert result["changed"] is True
    assert result["value_a"] == "postgres://localhost/db1"
    assert result["value_b"] == "postgres://localhost/db2"


def test_diff_versions_unchanged(vault_dir: str) -> None:
    """Same version compared against itself should report unchanged."""
    result = diff_versions(vault_dir, "DB_URL", PASSWORD, 1, 1)
    assert result["changed"] is False
    assert result["value_a"] == result["value_b"]


def test_diff_versions_missing_version(vault_dir: str) -> None:
    result = diff_versions(vault_dir, "DB_URL", PASSWORD, 1, 99)
    assert result["value_b"] is None
    assert result["changed"] is True


def test_diff_versions_missing_label(vault_dir: str) -> None:
    result = diff_versions(vault_dir, "UNKNOWN", PASSWORD, 1, 2)
    assert result["value_a"] is None
    assert result["value_b"] is None
    assert result["changed"] is False


def test_diff_labels_returns_all(vault_dir: str) -> None:
    mapping = diff_labels(vault_dir)
    assert "DB_URL" in mapping
    assert mapping["DB_URL"] == [1, 2]
    assert "API_KEY" in mapping
    assert mapping["API_KEY"] == [1]


def test_diff_labels_sorted(vault_dir: str) -> None:
    mapping = diff_labels(vault_dir)
    for versions in mapping.values():
        assert versions == sorted(versions)

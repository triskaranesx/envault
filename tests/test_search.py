"""Tests for envault.search module."""

import os
import pytest

from envault.vault import init_vault, add_entry
from envault.tags import add_tag
from envault.search import search_entries


PASSWORD = "test-pass"


@pytest.fixture()
def vault_dir(tmp_path):
    """Initialised vault with a handful of entries and tags."""
    d = str(tmp_path)
    init_vault(d, PASSWORD)
    add_entry(d, PASSWORD, "DB_HOST", "localhost")
    add_entry(d, PASSWORD, "DB_PORT", "5432")
    add_entry(d, PASSWORD, "API_KEY", "secret-key-123")
    add_entry(d, PASSWORD, "API_SECRET", "super-secret")
    add_tag(d, "DB_HOST", "database")
    add_tag(d, "DB_PORT", "database")
    add_tag(d, "API_KEY", "api")
    add_tag(d, "API_SECRET", "api")
    return d


def test_search_by_label_pattern(vault_dir):
    results = search_entries(vault_dir, PASSWORD, label_pattern="DB_*")
    labels = [r["label"] for r in results]
    assert "DB_HOST" in labels
    assert "DB_PORT" in labels
    assert "API_KEY" not in labels


def test_search_by_label_case_insensitive(vault_dir):
    results = search_entries(vault_dir, PASSWORD, label_pattern="db_*")
    assert len(results) == 2


def test_search_by_tag(vault_dir):
    results = search_entries(vault_dir, PASSWORD, tag="api")
    labels = [r["label"] for r in results]
    assert "API_KEY" in labels
    assert "API_SECRET" in labels
    assert "DB_HOST" not in labels


def test_search_by_value_pattern(vault_dir):
    results = search_entries(vault_dir, PASSWORD, value_pattern="*secret*")
    labels = [r["label"] for r in results]
    assert "API_SECRET" in labels
    assert "API_KEY" not in labels


def test_search_combined_filters(vault_dir):
    results = search_entries(
        vault_dir, PASSWORD, label_pattern="API_*", tag="api"
    )
    assert len(results) == 2


def test_search_no_match_returns_empty(vault_dir):
    results = search_entries(vault_dir, PASSWORD, label_pattern="NOPE_*")
    assert results == []


def test_search_result_includes_tags(vault_dir):
    results = search_entries(vault_dir, PASSWORD, label_pattern="DB_HOST")
    assert len(results) == 1
    assert "database" in results[0]["tags"]


def test_search_result_includes_value(vault_dir):
    results = search_entries(vault_dir, PASSWORD, label_pattern="DB_PORT")
    assert results[0]["value"] == "5432"

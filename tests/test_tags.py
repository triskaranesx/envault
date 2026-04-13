"""Tests for envault.tags module."""

import pytest
from pathlib import Path
from envault.tags import (
    add_tag,
    remove_tag,
    get_tags,
    find_by_tag,
    clear_tags_for_label,
)


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path)


def test_get_tags_empty(tmp_vault):
    assert get_tags(tmp_vault, "DB_PASSWORD") == []


def test_add_tag_creates_entry(tmp_vault):
    add_tag(tmp_vault, "DB_PASSWORD", "database")
    assert "database" in get_tags(tmp_vault, "DB_PASSWORD")


def test_add_tag_no_duplicates(tmp_vault):
    add_tag(tmp_vault, "API_KEY", "production")
    add_tag(tmp_vault, "API_KEY", "production")
    assert get_tags(tmp_vault, "API_KEY").count("production") == 1


def test_add_multiple_tags(tmp_vault):
    add_tag(tmp_vault, "API_KEY", "production")
    add_tag(tmp_vault, "API_KEY", "external")
    tags = get_tags(tmp_vault, "API_KEY")
    assert "production" in tags
    assert "external" in tags


def test_remove_tag_returns_true(tmp_vault):
    add_tag(tmp_vault, "SECRET", "sensitive")
    result = remove_tag(tmp_vault, "SECRET", "sensitive")
    assert result is True
    assert "sensitive" not in get_tags(tmp_vault, "SECRET")


def test_remove_tag_not_found_returns_false(tmp_vault):
    result = remove_tag(tmp_vault, "MISSING_LABEL", "nonexistent")
    assert result is False


def test_remove_last_tag_cleans_label(tmp_vault):
    add_tag(tmp_vault, "TOKEN", "temp")
    remove_tag(tmp_vault, "TOKEN", "temp")
    assert get_tags(tmp_vault, "TOKEN") == []


def test_find_by_tag_returns_matching_labels(tmp_vault):
    add_tag(tmp_vault, "DB_PASS", "database")
    add_tag(tmp_vault, "DB_HOST", "database")
    add_tag(tmp_vault, "API_KEY", "external")
    results = find_by_tag(tmp_vault, "database")
    assert "DB_PASS" in results
    assert "DB_HOST" in results
    assert "API_KEY" not in results


def test_find_by_tag_no_matches(tmp_vault):
    assert find_by_tag(tmp_vault, "nonexistent") == []


def test_clear_tags_for_label(tmp_vault):
    add_tag(tmp_vault, "SECRET", "sensitive")
    add_tag(tmp_vault, "SECRET", "production")
    clear_tags_for_label(tmp_vault, "SECRET")
    assert get_tags(tmp_vault, "SECRET") == []


def test_tags_persist_across_calls(tmp_vault):
    add_tag(tmp_vault, "PERSIST_KEY", "stable")
    assert "stable" in get_tags(tmp_vault, "PERSIST_KEY")

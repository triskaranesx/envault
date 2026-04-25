"""Tests for envault/env_category.py"""

from __future__ import annotations

import pytest

from envault.env_category import (
    CategoryError,
    find_by_category,
    get_category,
    list_categories,
    remove_category,
    set_category,
)


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_get_category_returns_none_when_absent(vault_dir):
    assert get_category(vault_dir, "MY_KEY") is None


def test_set_and_get_category(vault_dir):
    set_category(vault_dir, "MY_KEY", "database")
    assert get_category(vault_dir, "MY_KEY") == "database"


def test_set_category_overwrites_existing(vault_dir):
    set_category(vault_dir, "MY_KEY", "database")
    set_category(vault_dir, "MY_KEY", "auth")
    assert get_category(vault_dir, "MY_KEY") == "auth"


def test_set_category_empty_label_raises(vault_dir):
    with pytest.raises(CategoryError, match="Label"):
        set_category(vault_dir, "", "database")


def test_set_category_empty_category_raises(vault_dir):
    with pytest.raises(CategoryError, match="Category"):
        set_category(vault_dir, "MY_KEY", "")


def test_set_category_invalid_chars_raises(vault_dir):
    with pytest.raises(CategoryError, match="invalid characters"):
        set_category(vault_dir, "MY_KEY", "bad category!")


def test_set_category_hyphen_and_underscore_allowed(vault_dir):
    set_category(vault_dir, "MY_KEY", "my-category_1")
    assert get_category(vault_dir, "MY_KEY") == "my-category_1"


def test_remove_category_returns_true_when_existed(vault_dir):
    set_category(vault_dir, "MY_KEY", "database")
    assert remove_category(vault_dir, "MY_KEY") is True
    assert get_category(vault_dir, "MY_KEY") is None


def test_remove_category_returns_false_when_absent(vault_dir):
    assert remove_category(vault_dir, "MISSING") is False


def test_list_categories_empty(vault_dir):
    assert list_categories(vault_dir) == {}


def test_list_categories_returns_all(vault_dir):
    set_category(vault_dir, "A", "auth")
    set_category(vault_dir, "B", "database")
    result = list_categories(vault_dir)
    assert result == {"A": "auth", "B": "database"}


def test_find_by_category_returns_matching_labels(vault_dir):
    set_category(vault_dir, "A", "auth")
    set_category(vault_dir, "B", "database")
    set_category(vault_dir, "C", "auth")
    result = find_by_category(vault_dir, "auth")
    assert sorted(result) == ["A", "C"]


def test_find_by_category_case_insensitive(vault_dir):
    set_category(vault_dir, "X", "Auth")
    result = find_by_category(vault_dir, "auth")
    assert "X" in result


def test_find_by_category_returns_empty_when_none_match(vault_dir):
    set_category(vault_dir, "A", "database")
    assert find_by_category(vault_dir, "auth") == []

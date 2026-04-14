"""Tests for envault.env_defaults."""

from __future__ import annotations

import pytest

from envault.env_defaults import (
    clear_defaults,
    get_default,
    list_defaults,
    remove_default,
    set_default,
)


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_get_default_returns_none_when_absent(vault_dir):
    assert get_default(vault_dir, "DB_HOST") is None


def test_set_and_get_default(vault_dir):
    set_default(vault_dir, "DB_HOST", "localhost")
    assert get_default(vault_dir, "DB_HOST") == "localhost"


def test_set_default_overwrites_existing(vault_dir):
    set_default(vault_dir, "DB_PORT", "5432")
    set_default(vault_dir, "DB_PORT", "3306")
    assert get_default(vault_dir, "DB_PORT") == "3306"


def test_set_default_empty_label_raises(vault_dir):
    with pytest.raises(ValueError):
        set_default(vault_dir, "", "value")


def test_remove_default_returns_true_when_present(vault_dir):
    set_default(vault_dir, "API_KEY", "secret")
    assert remove_default(vault_dir, "API_KEY") is True
    assert get_default(vault_dir, "API_KEY") is None


def test_remove_default_returns_false_when_absent(vault_dir):
    assert remove_default(vault_dir, "NONEXISTENT") is False


def test_list_defaults_empty(vault_dir):
    assert list_defaults(vault_dir) == {}


def test_list_defaults_returns_all_entries(vault_dir):
    set_default(vault_dir, "FOO", "bar")
    set_default(vault_dir, "BAZ", "qux")
    result = list_defaults(vault_dir)
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_list_defaults_returns_copy(vault_dir):
    set_default(vault_dir, "X", "1")
    result = list_defaults(vault_dir)
    result["X"] = "mutated"
    assert get_default(vault_dir, "X") == "1"


def test_clear_defaults_returns_count(vault_dir):
    set_default(vault_dir, "A", "1")
    set_default(vault_dir, "B", "2")
    assert clear_defaults(vault_dir) == 2


def test_clear_defaults_removes_all(vault_dir):
    set_default(vault_dir, "A", "1")
    clear_defaults(vault_dir)
    assert list_defaults(vault_dir) == {}


def test_clear_defaults_empty_vault_returns_zero(vault_dir):
    assert clear_defaults(vault_dir) == 0

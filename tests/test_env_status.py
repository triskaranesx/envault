"""Tests for envault/env_status.py"""

import pytest
from pathlib import Path
from envault.env_status import (
    set_status,
    get_status,
    remove_status,
    list_statuses,
    find_by_status,
    StatusError,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_get_status_returns_none_when_absent(vault_dir):
    assert get_status(vault_dir, "MY_KEY") is None


def test_set_and_get_status(vault_dir):
    set_status(vault_dir, "MY_KEY", "active")
    assert get_status(vault_dir, "MY_KEY") == "active"


def test_set_status_case_insensitive(vault_dir):
    set_status(vault_dir, "MY_KEY", "DEPRECATED")
    assert get_status(vault_dir, "MY_KEY") == "deprecated"


def test_set_status_overwrites_existing(vault_dir):
    set_status(vault_dir, "MY_KEY", "active")
    set_status(vault_dir, "MY_KEY", "stable")
    assert get_status(vault_dir, "MY_KEY") == "stable"


def test_set_status_invalid_raises(vault_dir):
    with pytest.raises(StatusError, match="Invalid status"):
        set_status(vault_dir, "MY_KEY", "unknown")


def test_set_status_empty_label_raises(vault_dir):
    with pytest.raises(StatusError, match="empty"):
        set_status(vault_dir, "", "active")


def test_remove_status_returns_true_when_exists(vault_dir):
    set_status(vault_dir, "MY_KEY", "active")
    assert remove_status(vault_dir, "MY_KEY") is True
    assert get_status(vault_dir, "MY_KEY") is None


def test_remove_status_returns_false_when_absent(vault_dir):
    assert remove_status(vault_dir, "MISSING") is False


def test_list_statuses_empty(vault_dir):
    assert list_statuses(vault_dir) == {}


def test_list_statuses_multiple(vault_dir):
    set_status(vault_dir, "KEY_A", "active")
    set_status(vault_dir, "KEY_B", "deprecated")
    result = list_statuses(vault_dir)
    assert result == {"KEY_A": "active", "KEY_B": "deprecated"}


def test_find_by_status_returns_matching_labels(vault_dir):
    set_status(vault_dir, "KEY_A", "active")
    set_status(vault_dir, "KEY_B", "deprecated")
    set_status(vault_dir, "KEY_C", "active")
    result = find_by_status(vault_dir, "active")
    assert set(result) == {"KEY_A", "KEY_C"}


def test_find_by_status_empty_when_none_match(vault_dir):
    set_status(vault_dir, "KEY_A", "active")
    assert find_by_status(vault_dir, "experimental") == []


def test_status_file_created_on_first_set(vault_dir):
    set_status(vault_dir, "KEY", "stable")
    assert (Path(vault_dir) / ".envault_status.json").exists()


def test_all_valid_statuses_accepted(vault_dir):
    for s in ["active", "deprecated", "experimental", "stable"]:
        set_status(vault_dir, f"KEY_{s.upper()}", s)
        assert get_status(vault_dir, f"KEY_{s.upper()}") == s

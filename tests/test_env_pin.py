"""Tests for envault.env_pin module."""

import pytest
from pathlib import Path
from envault.env_pin import pin_entry, unpin_entry, get_pin, list_pins, check_pins


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_get_pin_returns_none_when_absent(vault_dir):
    assert get_pin(vault_dir, "MY_KEY") is None


def test_pin_entry_and_get(vault_dir):
    pin_entry(vault_dir, "MY_KEY", "abc123")
    assert get_pin(vault_dir, "MY_KEY") == "abc123"


def test_pin_entry_overwrites_existing(vault_dir):
    pin_entry(vault_dir, "MY_KEY", "first")
    pin_entry(vault_dir, "MY_KEY", "second")
    assert get_pin(vault_dir, "MY_KEY") == "second"


def test_pin_entry_empty_label_raises(vault_dir):
    with pytest.raises(ValueError, match="Label"):
        pin_entry(vault_dir, "", "value")


def test_pin_entry_none_value_raises(vault_dir):
    with pytest.raises(ValueError, match="value"):
        pin_entry(vault_dir, "KEY", None)


def test_unpin_entry_returns_true_when_existed(vault_dir):
    pin_entry(vault_dir, "MY_KEY", "val")
    assert unpin_entry(vault_dir, "MY_KEY") is True


def test_unpin_entry_returns_false_when_absent(vault_dir):
    assert unpin_entry(vault_dir, "GHOST") is False


def test_unpin_removes_entry(vault_dir):
    pin_entry(vault_dir, "MY_KEY", "val")
    unpin_entry(vault_dir, "MY_KEY")
    assert get_pin(vault_dir, "MY_KEY") is None


def test_list_pins_empty(vault_dir):
    assert list_pins(vault_dir) == {}


def test_list_pins_returns_all(vault_dir):
    pin_entry(vault_dir, "A", "1")
    pin_entry(vault_dir, "B", "2")
    pins = list_pins(vault_dir)
    assert pins == {"A": "1", "B": "2"}


def test_check_pins_no_violations(vault_dir):
    pin_entry(vault_dir, "KEY", "correct")
    violations = check_pins(vault_dir, {"KEY": "correct"})
    assert violations == []


def test_check_pins_detects_wrong_value(vault_dir):
    pin_entry(vault_dir, "KEY", "expected")
    violations = check_pins(vault_dir, {"KEY": "wrong"})
    assert len(violations) == 1
    assert violations[0]["label"] == "KEY"
    assert violations[0]["expected"] == "expected"
    assert violations[0]["actual"] == "wrong"


def test_check_pins_detects_missing_key(vault_dir):
    pin_entry(vault_dir, "REQUIRED", "value")
    violations = check_pins(vault_dir, {})
    assert len(violations) == 1
    assert violations[0]["actual"] is None


def test_check_pins_no_pins_no_violations(vault_dir):
    violations = check_pins(vault_dir, {"A": "1", "B": "2"})
    assert violations == []

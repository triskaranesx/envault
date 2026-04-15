"""Persistence and edge-case tests for envault.env_pin."""

import json
from pathlib import Path
import pytest
from envault.env_pin import pin_entry, unpin_entry, get_pin, list_pins, _pins_path


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_pins_file_created_on_first_pin(vault_dir):
    assert not _pins_path(vault_dir).exists()
    pin_entry(vault_dir, "K", "v")
    assert _pins_path(vault_dir).exists()


def test_pins_persisted_as_json(vault_dir):
    pin_entry(vault_dir, "KEY", "value")
    raw = json.loads(_pins_path(vault_dir).read_text())
    assert raw["KEY"] == "value"


def test_multiple_pins_stored_independently(vault_dir):
    pin_entry(vault_dir, "A", "1")
    pin_entry(vault_dir, "B", "2")
    pin_entry(vault_dir, "C", "3")
    assert get_pin(vault_dir, "A") == "1"
    assert get_pin(vault_dir, "B") == "2"
    assert get_pin(vault_dir, "C") == "3"


def test_unpin_does_not_affect_others(vault_dir):
    pin_entry(vault_dir, "A", "1")
    pin_entry(vault_dir, "B", "2")
    unpin_entry(vault_dir, "A")
    assert get_pin(vault_dir, "A") is None
    assert get_pin(vault_dir, "B") == "2"


def test_list_pins_is_copy(vault_dir):
    pin_entry(vault_dir, "K", "v")
    pins = list_pins(vault_dir)
    pins["K"] = "mutated"
    assert get_pin(vault_dir, "K") == "v"


def test_empty_string_value_is_valid_pin(vault_dir):
    pin_entry(vault_dir, "EMPTY", "")
    assert get_pin(vault_dir, "EMPTY") == ""


def test_pin_value_with_special_chars(vault_dir):
    special = "p@$$w0rd!#%&*()"
    pin_entry(vault_dir, "SECRET", special)
    assert get_pin(vault_dir, "SECRET") == special

"""Persistence tests for env_category: verifies JSON file structure."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.env_category import (
    remove_category,
    set_category,
)


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_categories_file_created_on_first_set(vault_dir):
    set_category(vault_dir, "KEY", "auth")
    assert (Path(vault_dir) / ".categories.json").exists()


def test_categories_persisted_as_json(vault_dir):
    set_category(vault_dir, "KEY", "auth")
    data = json.loads((Path(vault_dir) / ".categories.json").read_text())
    assert data == {"KEY": "auth"}


def test_multiple_categories_stored_independently(vault_dir):
    set_category(vault_dir, "A", "auth")
    set_category(vault_dir, "B", "database")
    data = json.loads((Path(vault_dir) / ".categories.json").read_text())
    assert data["A"] == "auth"
    assert data["B"] == "database"


def test_remove_does_not_affect_other_categories(vault_dir):
    set_category(vault_dir, "A", "auth")
    set_category(vault_dir, "B", "database")
    remove_category(vault_dir, "A")
    data = json.loads((Path(vault_dir) / ".categories.json").read_text())
    assert "A" not in data
    assert data["B"] == "database"


def test_json_structure_is_flat_dict(vault_dir):
    set_category(vault_dir, "X", "infra")
    data = json.loads((Path(vault_dir) / ".categories.json").read_text())
    assert isinstance(data, dict)
    for key, val in data.items():
        assert isinstance(key, str)
        assert isinstance(val, str)

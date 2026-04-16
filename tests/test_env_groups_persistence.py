"""Persistence tests for envault.env_groups."""
import json
from pathlib import Path
import pytest
from envault.env_groups import add_label_to_group, create_group, _groups_path


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_groups_file_created_on_first_add(vault_dir):
    add_label_to_group(vault_dir, "grp", "A")
    assert _groups_path(vault_dir).exists()


def test_groups_persisted_as_json(vault_dir):
    add_label_to_group(vault_dir, "grp", "A")
    raw = json.loads(_groups_path(vault_dir).read_text())
    assert "grp" in raw
    assert "A" in raw["grp"]


def test_multiple_groups_stored_independently(vault_dir):
    add_label_to_group(vault_dir, "g1", "KEY1")
    add_label_to_group(vault_dir, "g2", "KEY2")
    raw = json.loads(_groups_path(vault_dir).read_text())
    assert "KEY1" in raw["g1"]
    assert "KEY2" in raw["g2"]
    assert "KEY2" not in raw.get("g1", [])


def test_remove_does_not_affect_other_groups(vault_dir):
    from envault.env_groups import remove_label_from_group
    add_label_to_group(vault_dir, "g1", "X")
    add_label_to_group(vault_dir, "g2", "X")
    remove_label_from_group(vault_dir, "g1", "X")
    raw = json.loads(_groups_path(vault_dir).read_text())
    assert "X" not in raw["g1"]
    assert "X" in raw["g2"]


def test_create_group_does_not_overwrite_existing(vault_dir):
    add_label_to_group(vault_dir, "grp", "EXISTING")
    create_group(vault_dir, "grp")
    raw = json.loads(_groups_path(vault_dir).read_text())
    assert "EXISTING" in raw["grp"]

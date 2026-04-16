"""Tests for envault.env_groups."""
import pytest
from envault.env_groups import (
    create_group, delete_group, add_label_to_group,
    remove_label_from_group, get_group, list_groups, find_groups_for_label,
)


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_list_groups_empty(vault_dir):
    assert list_groups(vault_dir) == []


def test_create_group(vault_dir):
    create_group(vault_dir, "backend")
    assert "backend" in list_groups(vault_dir)


def test_create_group_empty_name_raises(vault_dir):
    with pytest.raises(ValueError):
        create_group(vault_dir, "  ")


def test_create_group_idempotent(vault_dir):
    create_group(vault_dir, "g")
    create_group(vault_dir, "g")
    assert list_groups(vault_dir).count("g") == 1


def test_get_group_returns_none_when_absent(vault_dir):
    assert get_group(vault_dir, "nope") is None


def test_get_group_returns_empty_list_after_create(vault_dir):
    create_group(vault_dir, "empty")
    assert get_group(vault_dir, "empty") == []


def test_add_label_to_group(vault_dir):
    add_label_to_group(vault_dir, "grp", "DB_URL")
    assert "DB_URL" in get_group(vault_dir, "grp")


def test_add_label_no_duplicates(vault_dir):
    add_label_to_group(vault_dir, "grp", "DB_URL")
    add_label_to_group(vault_dir, "grp", "DB_URL")
    assert get_group(vault_dir, "grp").count("DB_URL") == 1


def test_add_label_empty_group_name_raises(vault_dir):
    with pytest.raises(ValueError):
        add_label_to_group(vault_dir, "", "LABEL")


def test_remove_label_from_group(vault_dir):
    add_label_to_group(vault_dir, "grp", "KEY")
    remove_label_from_group(vault_dir, "grp", "KEY")
    assert "KEY" not in get_group(vault_dir, "grp")


def test_remove_label_not_present_is_noop(vault_dir):
    create_group(vault_dir, "grp")
    remove_label_from_group(vault_dir, "grp", "MISSING")
    assert get_group(vault_dir, "grp") == []


def test_delete_group(vault_dir):
    create_group(vault_dir, "tmp")
    delete_group(vault_dir, "tmp")
    assert "tmp" not in list_groups(vault_dir)


def test_delete_nonexistent_group_is_noop(vault_dir):
    delete_group(vault_dir, "ghost")


def test_find_groups_for_label(vault_dir):
    add_label_to_group(vault_dir, "a", "X")
    add_label_to_group(vault_dir, "b", "X")
    add_label_to_group(vault_dir, "c", "Y")
    result = find_groups_for_label(vault_dir, "X")
    assert set(result) == {"a", "b"}


def test_find_groups_returns_empty_when_label_absent(vault_dir):
    create_group(vault_dir, "grp")
    assert find_groups_for_label(vault_dir, "NOPE") == []

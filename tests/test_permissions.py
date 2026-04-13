"""Tests for envault.permissions module."""

import pytest
from pathlib import Path
from envault.permissions import (
    set_permission,
    get_permission,
    remove_permission,
    list_permissions,
    has_permission,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_get_permission_returns_none_when_absent(vault_dir):
    assert get_permission(vault_dir, "alice") is None


def test_set_and_get_permission(vault_dir):
    set_permission(vault_dir, "alice", "read")
    assert get_permission(vault_dir, "alice") == "read"


def test_set_permission_overwrites(vault_dir):
    set_permission(vault_dir, "alice", "read")
    set_permission(vault_dir, "alice", "admin")
    assert get_permission(vault_dir, "alice") == "admin"


def test_set_permission_invalid_role_raises(vault_dir):
    with pytest.raises(ValueError, match="Invalid role"):
        set_permission(vault_dir, "alice", "superuser")


def test_set_permission_empty_actor_raises(vault_dir):
    with pytest.raises(ValueError, match="Actor name"):
        set_permission(vault_dir, "", "read")


def test_set_permission_label_scoped(vault_dir):
    set_permission(vault_dir, "bob", "write", label="DB_PASS")
    assert get_permission(vault_dir, "bob", label="DB_PASS") == "write"
    assert get_permission(vault_dir, "bob") is None


def test_remove_permission_returns_true_when_exists(vault_dir):
    set_permission(vault_dir, "alice", "read")
    result = remove_permission(vault_dir, "alice")
    assert result is True
    assert get_permission(vault_dir, "alice") is None


def test_remove_permission_returns_false_when_absent(vault_dir):
    assert remove_permission(vault_dir, "ghost") is False


def test_list_permissions_empty(vault_dir):
    assert list_permissions(vault_dir) == []


def test_list_permissions_returns_all(vault_dir):
    set_permission(vault_dir, "alice", "admin")
    set_permission(vault_dir, "bob", "read")
    entries = list_permissions(vault_dir)
    actors = [e["actor"] for e in entries]
    assert "alice" in actors
    assert "bob" in actors


def test_has_permission_exact_role(vault_dir):
    set_permission(vault_dir, "alice", "write")
    assert has_permission(vault_dir, "alice", "write") is True


def test_has_permission_higher_role_satisfies(vault_dir):
    set_permission(vault_dir, "alice", "admin")
    assert has_permission(vault_dir, "alice", "read") is True
    assert has_permission(vault_dir, "alice", "write") is True


def test_has_permission_lower_role_fails(vault_dir):
    set_permission(vault_dir, "alice", "read")
    assert has_permission(vault_dir, "alice", "write") is False
    assert has_permission(vault_dir, "alice", "admin") is False


def test_has_permission_falls_back_to_vault_scope(vault_dir):
    set_permission(vault_dir, "alice", "write")
    assert has_permission(vault_dir, "alice", "read", label="SECRET") is True


def test_has_permission_no_role_returns_false(vault_dir):
    assert has_permission(vault_dir, "ghost", "read") is False

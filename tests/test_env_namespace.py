"""Tests for envault.env_namespace."""

import pytest
from click.testing import CliRunner
from envault.env_namespace import (
    set_namespace,
    get_namespace,
    remove_namespace,
    list_namespaces,
    get_labels_in_namespace,
    NamespaceError,
)
from envault.cli_namespace import cmd_namespace


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def runner():
    return CliRunner()


def test_get_namespace_returns_none_when_absent(vault_dir):
    assert get_namespace(vault_dir, "MY_KEY") is None


def test_set_and_get_namespace(vault_dir):
    set_namespace(vault_dir, "MY_KEY", "auth")
    assert get_namespace(vault_dir, "MY_KEY") == "auth"


def test_set_namespace_overwrites_existing(vault_dir):
    set_namespace(vault_dir, "MY_KEY", "auth")
    set_namespace(vault_dir, "MY_KEY", "billing")
    assert get_namespace(vault_dir, "MY_KEY") == "billing"


def test_set_namespace_empty_label_raises(vault_dir):
    with pytest.raises(NamespaceError):
        set_namespace(vault_dir, "", "auth")


def test_set_namespace_invalid_namespace_raises(vault_dir):
    with pytest.raises(NamespaceError):
        set_namespace(vault_dir, "KEY", "bad namespace!")


def test_remove_namespace_returns_true(vault_dir):
    set_namespace(vault_dir, "KEY", "auth")
    assert remove_namespace(vault_dir, "KEY") is True
    assert get_namespace(vault_dir, "KEY") is None


def test_remove_namespace_absent_returns_false(vault_dir):
    assert remove_namespace(vault_dir, "MISSING") is False


def test_list_namespaces_empty(vault_dir):
    assert list_namespaces(vault_dir) == {}


def test_list_namespaces_returns_all(vault_dir):
    set_namespace(vault_dir, "A", "auth")
    set_namespace(vault_dir, "B", "billing")
    data = list_namespaces(vault_dir)
    assert data == {"A": "auth", "B": "billing"}


def test_get_labels_in_namespace(vault_dir):
    set_namespace(vault_dir, "A", "auth")
    set_namespace(vault_dir, "B", "auth")
    set_namespace(vault_dir, "C", "billing")
    assert get_labels_in_namespace(vault_dir, "auth") == ["A", "B"]
    assert get_labels_in_namespace(vault_dir, "billing") == ["C"]


def test_get_labels_in_namespace_empty(vault_dir):
    assert get_labels_in_namespace(vault_dir, "nonexistent") == []


def test_cli_ns_set_and_get(vault_dir, runner):
    result = runner.invoke(cmd_namespace, ["set", "MY_KEY", "auth", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "auth" in result.output

    result = runner.invoke(cmd_namespace, ["get", "MY_KEY", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "auth" in result.output


def test_cli_ns_list_with_filter(vault_dir, runner):
    runner.invoke(cmd_namespace, ["set", "X", "ops", "--vault", vault_dir])
    runner.invoke(cmd_namespace, ["set", "Y", "ops", "--vault", vault_dir])
    result = runner.invoke(cmd_namespace, ["list", "--vault", vault_dir, "--ns", "ops"])
    assert result.exit_code == 0
    assert "X" in result.output
    assert "Y" in result.output


def test_cli_ns_remove(vault_dir, runner):
    runner.invoke(cmd_namespace, ["set", "Z", "auth", "--vault", vault_dir])
    result = runner.invoke(cmd_namespace, ["remove", "Z", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "Removed" in result.output

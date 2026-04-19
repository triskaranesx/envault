"""Tests for env_priority module."""
import pytest
from click.testing import CliRunner
from envault.env_priority import (
    set_priority, get_priority, remove_priority,
    list_priorities, find_by_priority,
)
from envault.cli_priority import cmd_priority


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture()
def runner():
    return CliRunner()


def test_get_priority_returns_none_when_absent(vault_dir):
    assert get_priority(vault_dir, "API_KEY") is None


def test_set_and_get_priority(vault_dir):
    set_priority(vault_dir, "API_KEY", "high")
    assert get_priority(vault_dir, "API_KEY") == "high"


def test_set_priority_overwrites_existing(vault_dir):
    set_priority(vault_dir, "API_KEY", "low")
    set_priority(vault_dir, "API_KEY", "critical")
    assert get_priority(vault_dir, "API_KEY") == "critical"


def test_set_priority_empty_label_raises(vault_dir):
    with pytest.raises(ValueError, match="label"):
        set_priority(vault_dir, "", "high")


def test_set_priority_invalid_priority_raises(vault_dir):
    with pytest.raises(ValueError, match="priority"):
        set_priority(vault_dir, "KEY", "urgent")


def test_remove_priority_returns_true(vault_dir):
    set_priority(vault_dir, "KEY", "normal")
    assert remove_priority(vault_dir, "KEY") is True
    assert get_priority(vault_dir, "KEY") is None


def test_remove_priority_missing_returns_false(vault_dir):
    assert remove_priority(vault_dir, "MISSING") is False


def test_list_priorities_empty(vault_dir):
    assert list_priorities(vault_dir) == []


def test_list_priorities_returns_all(vault_dir):
    set_priority(vault_dir, "A", "low")
    set_priority(vault_dir, "B", "critical")
    result = list_priorities(vault_dir)
    labels = [e["label"] for e in result]
    assert "A" in labels and "B" in labels


def test_find_by_priority(vault_dir):
    set_priority(vault_dir, "X", "high")
    set_priority(vault_dir, "Y", "low")
    assert find_by_priority(vault_dir, "high") == ["X"]


def test_find_by_priority_invalid_raises(vault_dir):
    with pytest.raises(ValueError):
        find_by_priority(vault_dir, "extreme")


def test_cli_priority_set(runner, vault_dir):
    result = runner.invoke(cmd_priority, ["set", "DB_PASS", "critical", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "critical" in result.output


def test_cli_priority_get_not_set(runner, vault_dir):
    result = runner.invoke(cmd_priority, ["get", "MISSING", "--vault", vault_dir])
    assert "No priority" in result.output


def test_cli_priority_list_empty(runner, vault_dir):
    result = runner.invoke(cmd_priority, ["list", "--vault", vault_dir])
    assert "No priorities" in result.output

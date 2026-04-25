"""Tests for envault.env_sensitivity."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.env_sensitivity import (
    SensitivityError,
    filter_by_level,
    get_sensitivity,
    list_sensitivity,
    remove_sensitivity,
    set_sensitivity,
)
from envault.cli_sensitivity import cmd_sensitivity


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture()
def runner():
    return CliRunner()


# --- unit tests ---

def test_get_sensitivity_returns_none_when_absent(vault_dir):
    assert get_sensitivity(vault_dir, "MY_KEY") is None


def test_set_and_get_sensitivity(vault_dir):
    set_sensitivity(vault_dir, "MY_KEY", "high")
    assert get_sensitivity(vault_dir, "MY_KEY") == "high"


def test_set_sensitivity_case_insensitive(vault_dir):
    set_sensitivity(vault_dir, "KEY", "CRITICAL")
    assert get_sensitivity(vault_dir, "KEY") == "critical"


def test_set_sensitivity_overwrites_existing(vault_dir):
    set_sensitivity(vault_dir, "KEY", "low")
    set_sensitivity(vault_dir, "KEY", "high")
    assert get_sensitivity(vault_dir, "KEY") == "high"


def test_set_sensitivity_invalid_level_raises(vault_dir):
    with pytest.raises(SensitivityError, match="invalid level"):
        set_sensitivity(vault_dir, "KEY", "extreme")


def test_set_sensitivity_empty_label_raises(vault_dir):
    with pytest.raises(SensitivityError, match="empty"):
        set_sensitivity(vault_dir, "", "low")


def test_remove_sensitivity_returns_true_when_present(vault_dir):
    set_sensitivity(vault_dir, "KEY", "medium")
    assert remove_sensitivity(vault_dir, "KEY") is True
    assert get_sensitivity(vault_dir, "KEY") is None


def test_remove_sensitivity_returns_false_when_absent(vault_dir):
    assert remove_sensitivity(vault_dir, "MISSING") is False


def test_list_sensitivity_empty(vault_dir):
    assert list_sensitivity(vault_dir) == []


def test_list_sensitivity_sorted(vault_dir):
    set_sensitivity(vault_dir, "Z_KEY", "low")
    set_sensitivity(vault_dir, "A_KEY", "critical")
    records = list_sensitivity(vault_dir)
    assert [r["label"] for r in records] == ["A_KEY", "Z_KEY"]


def test_filter_by_level(vault_dir):
    set_sensitivity(vault_dir, "A", "high")
    set_sensitivity(vault_dir, "B", "low")
    set_sensitivity(vault_dir, "C", "high")
    assert filter_by_level(vault_dir, "high") == ["A", "C"]
    assert filter_by_level(vault_dir, "low") == ["B"]


# --- CLI tests ---

def test_cli_sensitivity_set(runner, vault_dir):
    result = runner.invoke(cmd_sensitivity, ["set", "MY_KEY", "critical", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "critical" in result.output


def test_cli_sensitivity_get_shows_level(runner, vault_dir):
    set_sensitivity(vault_dir, "MY_KEY", "medium")
    result = runner.invoke(cmd_sensitivity, ["get", "MY_KEY", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "medium" in result.output


def test_cli_sensitivity_get_not_set(runner, vault_dir):
    result = runner.invoke(cmd_sensitivity, ["get", "GHOST", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No sensitivity" in result.output


def test_cli_sensitivity_list_filtered(runner, vault_dir):
    set_sensitivity(vault_dir, "A", "high")
    set_sensitivity(vault_dir, "B", "low")
    result = runner.invoke(cmd_sensitivity, ["list", "--vault-dir", vault_dir, "--level", "high"])
    assert result.exit_code == 0
    assert "A" in result.output
    assert "B" not in result.output

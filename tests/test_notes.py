"""Tests for envault.notes and envault.cli_notes."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.notes import get_note, list_notes, remove_note, set_note
from envault.cli_notes import cmd_notes


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture()
def runner():
    return CliRunner()


# --- unit tests for notes module ---

def test_get_note_returns_none_when_absent(vault_dir):
    assert get_note(vault_dir, "MY_KEY") is None


def test_set_and_get_note(vault_dir):
    set_note(vault_dir, "MY_KEY", "This is a test note.")
    assert get_note(vault_dir, "MY_KEY") == "This is a test note."


def test_set_note_overwrites_existing(vault_dir):
    set_note(vault_dir, "KEY", "first")
    set_note(vault_dir, "KEY", "second")
    assert get_note(vault_dir, "KEY") == "second"


def test_set_note_empty_label_raises(vault_dir):
    with pytest.raises(ValueError):
        set_note(vault_dir, "", "some note")


def test_remove_note_returns_true_when_present(vault_dir):
    set_note(vault_dir, "KEY", "hello")
    assert remove_note(vault_dir, "KEY") is True
    assert get_note(vault_dir, "KEY") is None


def test_remove_note_returns_false_when_absent(vault_dir):
    assert remove_note(vault_dir, "MISSING") is False


def test_list_notes_empty(vault_dir):
    assert list_notes(vault_dir) == {}


def test_list_notes_returns_all(vault_dir):
    set_note(vault_dir, "A", "note-a")
    set_note(vault_dir, "B", "note-b")
    result = list_notes(vault_dir)
    assert result == {"A": "note-a", "B": "note-b"}


# --- CLI tests ---

def test_cli_note_set(runner, vault_dir):
    result = runner.invoke(cmd_notes, ["set", "DB_URL", "prod db", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "Note set" in result.output
    assert get_note(vault_dir, "DB_URL") == "prod db"


def test_cli_note_get_present(runner, vault_dir):
    set_note(vault_dir, "API_KEY", "keep secret")
    result = runner.invoke(cmd_notes, ["get", "API_KEY", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "keep secret" in result.output


def test_cli_note_get_absent(runner, vault_dir):
    result = runner.invoke(cmd_notes, ["get", "NOPE", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "No note found" in result.output


def test_cli_note_remove(runner, vault_dir):
    set_note(vault_dir, "X", "bye")
    result = runner.invoke(cmd_notes, ["remove", "X", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_cli_note_list(runner, vault_dir):
    set_note(vault_dir, "Z", "zzz")
    result = runner.invoke(cmd_notes, ["list", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "Z: zzz" in result.output

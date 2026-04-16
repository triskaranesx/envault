"""Tests for envault template management."""

import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.templates import save_template, get_template, delete_template, list_templates
from envault.cli_templates import cmd_template


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def runner():
    return CliRunner()


def test_save_and_get_template(vault_dir):
    save_template(vault_dir, "backend", ["DB_URL", "SECRET_KEY"])
    labels = get_template(vault_dir, "backend")
    assert labels == ["DB_URL", "SECRET_KEY"]


def test_get_nonexistent_template_returns_none(vault_dir):
    assert get_template(vault_dir, "missing") is None


def test_save_template_empty_labels_raises(vault_dir):
    with pytest.raises(ValueError):
        save_template(vault_dir, "empty", [])


def test_save_template_overwrites_existing(vault_dir):
    """Saving a template with the same name should replace the old labels."""
    save_template(vault_dir, "overwrite", ["OLD_KEY"])
    save_template(vault_dir, "overwrite", ["NEW_KEY1", "NEW_KEY2"])
    labels = get_template(vault_dir, "overwrite")
    assert labels == ["NEW_KEY1", "NEW_KEY2"]


def test_delete_template_returns_true(vault_dir):
    save_template(vault_dir, "to_delete", ["FOO"])
    result = delete_template(vault_dir, "to_delete")
    assert result is True
    assert get_template(vault_dir, "to_delete") is None


def test_delete_nonexistent_returns_false(vault_dir):
    assert delete_template(vault_dir, "ghost") is False


def test_list_templates_returns_all(vault_dir):
    save_template(vault_dir, "a", ["X"])
    save_template(vault_dir, "b", ["Y", "Z"])
    templates = list_templates(vault_dir)
    assert "a" in templates
    assert "b" in templates
    assert templates["b"] == ["Y", "Z"]


def test_list_templates_empty(vault_dir):
    assert list_templates(vault_dir) == {}


def test_cli_template_save(runner, vault_dir):
    result = runner.invoke(cmd_template, ["save", "mytemplate", "KEY1", "KEY2", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "mytemplate" in result.output
    assert "2 label" in result.output


def test_cli_template_show(runner, vault_dir):
    save_template(vault_dir, "show_test", ["ALPHA", "BETA"])
    result = runner.invoke(cmd_template, ["show", "show_test", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "ALPHA" in result.output
    assert "BETA" in result.output


def test_cli_template_show_missing(runner, vault_dir):
    result = runner.invoke(cmd_template, ["show", "no_such", "--vault", vault_dir])
    assert result.exit_code != 0


def test_cli_template_delete(runner, vault_dir):
    save_template(vault_dir, "del_me", ["K"])
    result = runner.invoke(cmd_template, ["delete", "del_me", "--vault", vault_dir])
    assert result.exit_code == 0
    assert get_template(vault_dir, "del_me") is None


def test_cli_template_list(runner, vault_dir):
    save_template(vault_dir, "t1", ["A"])
    save_template(vault_dir, "t2", ["B"])
    result = runner.invoke(cmd_template, ["list", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "t1" in result.output
    assert "t2" in result.output

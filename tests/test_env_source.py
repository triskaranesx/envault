"""Tests for envault.env_source."""

import pytest
from pathlib import Path
from click.testing import CliRunner
from envault.env_source import (
    set_source,
    get_source,
    remove_source,
    list_sources,
    filter_by_source_type,
    SourceError,
)
from envault.cli_source import cmd_source


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def runner():
    return CliRunner()


def test_get_source_returns_none_when_absent(vault_dir):
    assert get_source(vault_dir, "MY_KEY") is None


def test_set_and_get_source(vault_dir):
    record = set_source(vault_dir, "MY_KEY", "manual")
    assert record["type"] == "manual"
    fetched = get_source(vault_dir, "MY_KEY")
    assert fetched == {"type": "manual"}


def test_set_source_with_origin(vault_dir):
    set_source(vault_dir, "API_KEY", "import", origin=".env.production")
    record = get_source(vault_dir, "API_KEY")
    assert record["type"] == "import"
    assert record["origin"] == ".env.production"


def test_set_source_overwrites_existing(vault_dir):
    set_source(vault_dir, "KEY", "manual")
    set_source(vault_dir, "KEY", "generated", origin="script.py")
    record = get_source(vault_dir, "KEY")
    assert record["type"] == "generated"
    assert record["origin"] == "script.py"


def test_set_source_invalid_type_raises(vault_dir):
    with pytest.raises(SourceError, match="Invalid source type"):
        set_source(vault_dir, "KEY", "unknown")


def test_set_source_empty_label_raises(vault_dir):
    with pytest.raises(SourceError, match="Label must not be empty"):
        set_source(vault_dir, "", "manual")


def test_remove_source_returns_true_when_present(vault_dir):
    set_source(vault_dir, "KEY", "sync")
    assert remove_source(vault_dir, "KEY") is True
    assert get_source(vault_dir, "KEY") is None


def test_remove_source_returns_false_when_absent(vault_dir):
    assert remove_source(vault_dir, "MISSING") is False


def test_list_sources_empty(vault_dir):
    assert list_sources(vault_dir) == {}


def test_list_sources_returns_all(vault_dir):
    set_source(vault_dir, "A", "manual")
    set_source(vault_dir, "B", "import", origin="file.env")
    result = list_sources(vault_dir)
    assert set(result.keys()) == {"A", "B"}


def test_filter_by_source_type(vault_dir):
    set_source(vault_dir, "A", "manual")
    set_source(vault_dir, "B", "import")
    set_source(vault_dir, "C", "manual")
    result = filter_by_source_type(vault_dir, "manual")
    assert set(result.keys()) == {"A", "C"}


def test_cli_source_set_success(runner, vault_dir):
    result = runner.invoke(cmd_source, ["set", "MY_KEY", "generated", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "Source set" in result.output


def test_cli_source_get_shows_value(runner, vault_dir):
    set_source(vault_dir, "MY_KEY", "sync", origin="remote")
    result = runner.invoke(cmd_source, ["get", "MY_KEY", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "sync" in result.output
    assert "remote" in result.output


def test_cli_source_list_filtered(runner, vault_dir):
    set_source(vault_dir, "A", "manual")
    set_source(vault_dir, "B", "import")
    result = runner.invoke(cmd_source, ["list", "--type", "manual", "--vault", vault_dir])
    assert result.exit_code == 0
    assert "A" in result.output
    assert "B" not in result.output

"""Tests for CLI tag commands."""

import pytest
from click.testing import CliRunner
from envault.cli_tags import cmd_tags


@pytest.fixture
def runner():
    return CliRunner()


def test_tag_add(runner, tmp_path):
    result = runner.invoke(
        cmd_tags, ["add", "DB_PASS", "database", "--vault", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "added" in result.output


def test_tag_list_shows_tags(runner, tmp_path):
    runner.invoke(cmd_tags, ["add", "API_KEY", "production", "--vault", str(tmp_path)])
    runner.invoke(cmd_tags, ["add", "API_KEY", "external", "--vault", str(tmp_path)])
    result = runner.invoke(cmd_tags, ["list", "API_KEY", "--vault", str(tmp_path)])
    assert result.exit_code == 0
    assert "production" in result.output
    assert "external" in result.output


def test_tag_list_empty(runner, tmp_path):
    result = runner.invoke(cmd_tags, ["list", "MISSING", "--vault", str(tmp_path)])
    assert result.exit_code == 0
    assert "No tags" in result.output


def test_tag_remove(runner, tmp_path):
    runner.invoke(cmd_tags, ["add", "SECRET", "sensitive", "--vault", str(tmp_path)])
    result = runner.invoke(
        cmd_tags, ["remove", "SECRET", "sensitive", "--vault", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "removed" in result.output


def test_tag_remove_not_found(runner, tmp_path):
    result = runner.invoke(
        cmd_tags, ["remove", "GHOST", "nope", "--vault", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "not found" in result.output


def test_tag_find(runner, tmp_path):
    runner.invoke(cmd_tags, ["add", "DB_PASS", "database", "--vault", str(tmp_path)])
    runner.invoke(cmd_tags, ["add", "DB_HOST", "database", "--vault", str(tmp_path)])
    result = runner.invoke(cmd_tags, ["find", "database", "--vault", str(tmp_path)])
    assert result.exit_code == 0
    assert "DB_PASS" in result.output
    assert "DB_HOST" in result.output


def test_tag_find_no_matches(runner, tmp_path):
    result = runner.invoke(cmd_tags, ["find", "ghost", "--vault", str(tmp_path)])
    assert result.exit_code == 0
    assert "No entries" in result.output


def test_tag_clear(runner, tmp_path):
    runner.invoke(cmd_tags, ["add", "TOKEN", "temp", "--vault", str(tmp_path)])
    result = runner.invoke(cmd_tags, ["clear", "TOKEN", "--vault", str(tmp_path)])
    assert result.exit_code == 0
    assert "cleared" in result.output

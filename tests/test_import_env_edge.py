"""Edge-case tests for envault.import_env.parse_env_file."""

from __future__ import annotations

from pathlib import Path

import pytest

from envault.import_env import parse_env_file


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / ".env"
    p.write_text(content)
    return p


def test_empty_file_returns_empty_list(tmp_path: Path) -> None:
    p = _write(tmp_path, "")
    assert parse_env_file(p) == []


def test_only_comments_returns_empty(tmp_path: Path) -> None:
    p = _write(tmp_path, "# just a comment\n# another\n")
    assert parse_env_file(p) == []


def test_value_with_equals_sign(tmp_path: Path) -> None:
    p = _write(tmp_path, 'TOKEN=abc=def==\n')
    pairs = dict(parse_env_file(p))
    assert pairs["TOKEN"] == "abc=def=="


def test_inline_comment_stripped(tmp_path: Path) -> None:
    p = _write(tmp_path, "PORT=8080 # http port\n")
    pairs = dict(parse_env_file(p))
    assert pairs["PORT"] == "8080"


def test_blank_lines_ignored(tmp_path: Path) -> None:
    content = "\nFOO=bar\n\nBAZ=qux\n\n"
    p = _write(tmp_path, content)
    pairs = parse_env_file(p)
    assert len(pairs) == 2


def test_double_quoted_value_with_spaces(tmp_path: Path) -> None:
    p = _write(tmp_path, 'MSG="hello world"\n')
    pairs = dict(parse_env_file(p))
    assert pairs["MSG"] == "hello world"


def test_single_quoted_value(tmp_path: Path) -> None:
    p = _write(tmp_path, "KEY='my value'\n")
    pairs = dict(parse_env_file(p))
    assert pairs["KEY"] == "my value"


def test_key_with_underscores_and_numbers(tmp_path: Path) -> None:
    p = _write(tmp_path, "MY_VAR_2=ok\n")
    pairs = dict(parse_env_file(p))
    assert "MY_VAR_2" in pairs

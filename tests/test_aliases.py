"""
tests/test_aliases.py — Tests for envault/aliases.py
"""

import pytest
from pathlib import Path
from envault.aliases import (
    set_alias,
    get_alias,
    remove_alias,
    list_aliases,
    resolve,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_get_alias_returns_none_when_absent(vault_dir):
    assert get_alias(vault_dir, "db") is None


def test_set_and_get_alias(vault_dir):
    set_alias(vault_dir, "db", "DATABASE_URL")
    assert get_alias(vault_dir, "db") == "DATABASE_URL"


def test_set_alias_overwrites_existing(vault_dir):
    set_alias(vault_dir, "db", "DATABASE_URL")
    set_alias(vault_dir, "db", "POSTGRES_URL")
    assert get_alias(vault_dir, "db") == "POSTGRES_URL"


def test_set_alias_empty_alias_raises(vault_dir):
    with pytest.raises(ValueError):
        set_alias(vault_dir, "", "DATABASE_URL")


def test_set_alias_empty_label_raises(vault_dir):
    with pytest.raises(ValueError):
        set_alias(vault_dir, "db", "")


def test_remove_alias_returns_true_when_exists(vault_dir):
    set_alias(vault_dir, "db", "DATABASE_URL")
    assert remove_alias(vault_dir, "db") is True
    assert get_alias(vault_dir, "db") is None


def test_remove_alias_returns_false_when_absent(vault_dir):
    assert remove_alias(vault_dir, "nonexistent") is False


def test_list_aliases_empty(vault_dir):
    assert list_aliases(vault_dir) == {}


def test_list_aliases_returns_all(vault_dir):
    set_alias(vault_dir, "db", "DATABASE_URL")
    set_alias(vault_dir, "key", "SECRET_KEY")
    result = list_aliases(vault_dir)
    assert result == {"db": "DATABASE_URL", "key": "SECRET_KEY"}


def test_resolve_known_alias(vault_dir):
    set_alias(vault_dir, "db", "DATABASE_URL")
    assert resolve(vault_dir, "db") == "DATABASE_URL"


def test_resolve_unknown_returns_input(vault_dir):
    assert resolve(vault_dir, "DATABASE_URL") == "DATABASE_URL"


def test_aliases_persisted_to_disk(vault_dir):
    set_alias(vault_dir, "s3", "S3_BUCKET")
    aliases_file = Path(vault_dir) / "aliases.json"
    assert aliases_file.exists()
    result = list_aliases(vault_dir)
    assert result["s3"] == "S3_BUCKET"

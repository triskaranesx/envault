"""Tests for envault/profiles.py"""

import pytest
from pathlib import Path
from envault.profiles import (
    save_profile,
    get_profile,
    delete_profile,
    list_profiles,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_get_profile_returns_none_when_absent(vault_dir):
    assert get_profile(vault_dir, "prod") is None


def test_save_and_get_profile(vault_dir):
    save_profile(vault_dir, "prod", ["DB_URL", "API_KEY"])
    result = get_profile(vault_dir, "prod")
    assert result == ["DB_URL", "API_KEY"]


def test_save_profile_overwrites_existing(vault_dir):
    save_profile(vault_dir, "dev", ["DEBUG"])
    save_profile(vault_dir, "dev", ["DEBUG", "LOG_LEVEL"])
    result = get_profile(vault_dir, "dev")
    assert result == ["DEBUG", "LOG_LEVEL"]


def test_save_profile_empty_name_raises(vault_dir):
    with pytest.raises(ValueError, match="empty"):
        save_profile(vault_dir, "", ["DB_URL"])


def test_save_profile_empty_labels_raises(vault_dir):
    with pytest.raises(ValueError, match="at least one label"):
        save_profile(vault_dir, "prod", [])


def test_delete_profile_returns_true(vault_dir):
    save_profile(vault_dir, "staging", ["S3_BUCKET"])
    assert delete_profile(vault_dir, "staging") is True
    assert get_profile(vault_dir, "staging") is None


def test_delete_profile_nonexistent_returns_false(vault_dir):
    assert delete_profile(vault_dir, "ghost") is False


def test_list_profiles_empty(vault_dir):
    assert list_profiles(vault_dir) == []


def test_list_profiles_sorted(vault_dir):
    save_profile(vault_dir, "prod", ["A"])
    save_profile(vault_dir, "dev", ["B"])
    save_profile(vault_dir, "staging", ["C"])
    assert list_profiles(vault_dir) == ["dev", "prod", "staging"]


def test_profiles_persisted_across_calls(vault_dir):
    save_profile(vault_dir, "ci", ["CI_TOKEN", "BUILD_NUM"])
    # Simulate fresh load by calling get again
    result = get_profile(vault_dir, "ci")
    assert "CI_TOKEN" in result
    assert "BUILD_NUM" in result

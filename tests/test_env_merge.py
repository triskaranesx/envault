"""Tests for envault.env_merge."""
import pytest

from envault.vault import init_vault, add_entry, get_entry
from envault.env_merge import merge_vaults, MergeResult


PASSWORD = "s3cret"


@pytest.fixture()
def base_vault(tmp_path):
    p = tmp_path / "base"
    p.mkdir()
    init_vault(str(p))
    add_entry(str(p), "DB_HOST", "localhost", PASSWORD)
    add_entry(str(p), "API_KEY", "base-key", PASSWORD)
    return str(p)


@pytest.fixture()
def other_vault(tmp_path):
    p = tmp_path / "other"
    p.mkdir()
    init_vault(str(p))
    add_entry(str(p), "API_KEY", "other-key", PASSWORD)   # conflict
    add_entry(str(p), "NEW_VAR", "hello", PASSWORD)        # new
    return str(p)


def test_merge_adds_new_labels(base_vault, other_vault):
    result = merge_vaults(base_vault, other_vault, PASSWORD, strategy="ours")
    assert "NEW_VAR" in result.added
    assert get_entry(base_vault, "NEW_VAR", PASSWORD) == "hello"


def test_merge_strategy_ours_keeps_base(base_vault, other_vault):
    result = merge_vaults(base_vault, other_vault, PASSWORD, strategy="ours")
    assert "API_KEY" in result.skipped
    assert get_entry(base_vault, "API_KEY", PASSWORD) == "base-key"


def test_merge_strategy_theirs_overwrites(base_vault, other_vault):
    result = merge_vaults(base_vault, other_vault, PASSWORD, strategy="theirs")
    assert "API_KEY" in result.updated
    assert get_entry(base_vault, "API_KEY", PASSWORD) == "other-key"


def test_merge_strategy_newest_picks_higher_version(base_vault, other_vault):
    # other_vault has version 1 for API_KEY; base also version 1 → skipped
    result = merge_vaults(base_vault, other_vault, PASSWORD, strategy="newest")
    assert "API_KEY" in result.skipped


def test_merge_strategy_error_records_conflict(base_vault, other_vault):
    # Add a second version to other_vault so versions differ
    add_entry(other_vault, "API_KEY", "other-key-v2", PASSWORD)
    result = merge_vaults(base_vault, other_vault, PASSWORD, strategy="error")
    conflict_labels = [c.label for c in result.conflicts]
    assert "API_KEY" in conflict_labels


def test_merge_result_is_named_tuple(base_vault, other_vault):
    result = merge_vaults(base_vault, other_vault, PASSWORD)
    assert isinstance(result, MergeResult)
    assert isinstance(result.added, list)
    assert isinstance(result.updated, list)
    assert isinstance(result.skipped, list)
    assert isinstance(result.conflicts, list)


def test_merge_does_not_touch_untouched_labels(base_vault, other_vault):
    merge_vaults(base_vault, other_vault, PASSWORD, strategy="theirs")
    # DB_HOST only exists in base, should remain intact
    assert get_entry(base_vault, "DB_HOST", PASSWORD) == "localhost"

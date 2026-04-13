"""Tests for envault.snapshots module and CLI."""

import json
import pytest
from pathlib import Path
from click.testing import CliRunner

from envault.snapshots import (
    save_snapshot,
    get_snapshot,
    list_snapshots,
    restore_snapshot,
    delete_snapshot,
)
from envault.cli_snapshots import cmd_snapshot


@pytest.fixture
def vault_dir(tmp_path):
    vault_data = {
        "version": 1,
        "entries": [
            {"index": 0, "label": "DB_PASS", "blob": "abc"},
            {"index": 1, "label": "API_KEY", "blob": "def"},
        ],
    }
    (tmp_path / "vault.json").write_text(json.dumps(vault_data))
    return str(tmp_path)


@pytest.fixture
def runner():
    return CliRunner()


def test_save_snapshot_returns_timestamp(vault_dir):
    ts = save_snapshot(vault_dir, "v1")
    assert "T" in ts  # ISO format contains T


def test_save_snapshot_creates_entry(vault_dir):
    save_snapshot(vault_dir, "v1")
    snap = get_snapshot(vault_dir, "v1")
    assert snap is not None
    assert "created_at" in snap
    assert len(snap["vault"]["entries"]) == 2


def test_get_snapshot_returns_none_when_absent(vault_dir):
    assert get_snapshot(vault_dir, "nonexistent") is None


def test_save_snapshot_empty_name_raises(vault_dir):
    with pytest.raises(ValueError):
        save_snapshot(vault_dir, "")


def test_save_snapshot_no_vault_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        save_snapshot(str(tmp_path), "v1")


def test_list_snapshots_sorted(vault_dir):
    save_snapshot(vault_dir, "alpha")
    save_snapshot(vault_dir, "beta")
    snaps = list_snapshots(vault_dir)
    assert [s["name"] for s in snaps] == ["alpha", "beta"]


def test_restore_snapshot_writes_vault(vault_dir):
    save_snapshot(vault_dir, "saved")
    # Overwrite vault with fewer entries
    new_data = {"version": 1, "entries": []}
    (Path(vault_dir) / "vault.json").write_text(json.dumps(new_data))
    count = restore_snapshot(vault_dir, "saved")
    assert count == 2
    restored = json.loads((Path(vault_dir) / "vault.json").read_text())
    assert len(restored["entries"]) == 2


def test_restore_snapshot_missing_raises(vault_dir):
    with pytest.raises(KeyError):
        restore_snapshot(vault_dir, "ghost")


def test_delete_snapshot_returns_true(vault_dir):
    save_snapshot(vault_dir, "temp")
    assert delete_snapshot(vault_dir, "temp") is True
    assert get_snapshot(vault_dir, "temp") is None


def test_delete_snapshot_missing_returns_false(vault_dir):
    assert delete_snapshot(vault_dir, "nope") is False


def test_cli_snapshot_save(runner, vault_dir):
    result = runner.invoke(cmd_snapshot, ["save", "v1", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "saved" in result.output


def test_cli_snapshot_list(runner, vault_dir):
    save_snapshot(vault_dir, "snap1")
    result = runner.invoke(cmd_snapshot, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "snap1" in result.output


def test_cli_snapshot_restore(runner, vault_dir):
    save_snapshot(vault_dir, "s1")
    result = runner.invoke(cmd_snapshot, ["restore", "s1", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "Restored" in result.output


def test_cli_snapshot_delete(runner, vault_dir):
    save_snapshot(vault_dir, "old")
    result = runner.invoke(cmd_snapshot, ["delete", "old", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "deleted" in result.output

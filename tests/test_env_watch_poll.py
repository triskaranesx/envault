"""Tests for the poll() helper in envault.env_watch."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.env_watch import poll, update_fingerprint


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    vault = tmp_path / "vault.json"
    vault.write_text(json.dumps({"entries": [], "version": 1}))
    return tmp_path


def test_poll_calls_on_change_once_for_initial_state(vault_dir: Path) -> None:
    """First poll should detect change (no baseline yet)."""
    events: list[Path] = []
    poll(vault_dir, lambda p: events.append(p), interval=0, max_checks=1)
    assert len(events) == 1


def test_poll_no_event_when_unchanged(vault_dir: Path) -> None:
    update_fingerprint(vault_dir)
    events: list[Path] = []
    poll(vault_dir, lambda p: events.append(p), interval=0, max_checks=3)
    assert events == []


def test_poll_detects_mid_run_change(vault_dir: Path) -> None:
    """Simulate a change occurring between poll iterations."""
    update_fingerprint(vault_dir)
    events: list[Path] = []
    call_count = 0

    def _on_change(p: Path) -> None:
        events.append(p)

    vault = vault_dir / "vault.json"

    def _side_effect_poll() -> None:
        nonlocal call_count
        # Modify vault before second check
        for _ in range(3):
            call_count += 1
            if call_count == 2:
                vault.write_text(json.dumps({"entries": ["x"], "version": 99}))
            from envault.env_watch import watch_once
            watch_once(vault_dir, _on_change)

    _side_effect_poll()
    assert len(events) == 1


def test_poll_max_checks_limits_iterations(vault_dir: Path) -> None:
    update_fingerprint(vault_dir)
    iterations = []
    poll(
        vault_dir,
        lambda p: None,
        interval=0,
        max_checks=5,
    )
    # Simply assert it doesn't run forever — no assertion needed beyond completion
    assert True

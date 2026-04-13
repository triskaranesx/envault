"""Tests for envault.sharing — export, import, and merge."""

import pytest
from envault.sharing import export_snapshot, import_snapshot, merge_entries

PASSWORD = "correct-horse-battery"

SAMPLE_VAULT = {
    "entries": [
        {"label": "production", "version": 1, "ciphertext": "abc123"},
        {"label": "staging", "version": 1, "ciphertext": "def456"},
    ]
}


def test_export_returns_string():
    token = export_snapshot(SAMPLE_VAULT, PASSWORD)
    assert isinstance(token, str)
    assert len(token) > 0


def test_export_import_roundtrip():
    token = export_snapshot(SAMPLE_VAULT, PASSWORD, label="my-snapshot")
    payload = import_snapshot(token, PASSWORD)
    assert payload["entries"] == SAMPLE_VAULT["entries"]
    assert payload["label"] == "my-snapshot"
    assert "exported_at" in payload


def test_export_two_tokens_differ():
    t1 = export_snapshot(SAMPLE_VAULT, PASSWORD)
    t2 = export_snapshot(SAMPLE_VAULT, PASSWORD)
    assert t1 != t2


def test_import_wrong_password_raises():
    token = export_snapshot(SAMPLE_VAULT, PASSWORD)
    with pytest.raises(ValueError, match="Decryption failed"):
        import_snapshot(token, "wrong-password")


def test_import_corrupted_token_raises():
    with pytest.raises(ValueError, match="Invalid share token format"):
        import_snapshot("not-a-valid-token!!", PASSWORD)


def test_import_wrong_version_raises():
    import base64, json
    envelope = json.dumps({"version": 99, "blob": "x"})
    token = base64.b64encode(envelope.encode()).decode()
    with pytest.raises(ValueError, match="Unsupported share format version"):
        import_snapshot(token, PASSWORD)


def test_merge_entries_no_duplicates():
    base = [{"label": "prod", "version": 1, "ciphertext": "aaa"}]
    incoming = [
        {"label": "prod", "version": 1, "ciphertext": "aaa"},  # duplicate
        {"label": "staging", "version": 1, "ciphertext": "bbb"},  # new
    ]
    merged = merge_entries(base, incoming)
    assert len(merged) == 2
    labels = [e["label"] for e in merged]
    assert "prod" in labels
    assert "staging" in labels


def test_merge_entries_different_versions_kept():
    base = [{"label": "prod", "version": 1, "ciphertext": "aaa"}]
    incoming = [{"label": "prod", "version": 2, "ciphertext": "bbb"}]
    merged = merge_entries(base, incoming)
    assert len(merged) == 2


def test_merge_empty_incoming():
    base = [{"label": "prod", "version": 1, "ciphertext": "aaa"}]
    merged = merge_entries(base, [])
    assert merged == base

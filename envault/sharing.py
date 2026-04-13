"""Team sharing support: export and import encrypted vault snapshots."""

import json
import base64
from datetime import datetime, timezone
from typing import Optional

from envault.crypto import encrypt, decrypt

SHARE_FORMAT_VERSION = 1


def export_snapshot(vault: dict, password: str, label: Optional[str] = None) -> str:
    """Serialize and encrypt a vault snapshot for sharing.

    Returns a base64-encoded string suitable for sharing with teammates.
    """
    payload = {
        "entries": vault.get("entries", []),
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "label": label or "",
    }
    raw = json.dumps(payload, separators=(",", ":"))
    encrypted = encrypt(raw, password)
    envelope = {
        "version": SHARE_FORMAT_VERSION,
        "blob": encrypted,
    }
    return base64.b64encode(json.dumps(envelope).encode()).decode()


def import_snapshot(token: str, password: str) -> dict:
    """Decrypt and deserialize a shared vault snapshot.

    Returns the payload dict with keys: entries, exported_at, label.
    Raises ValueError on bad token format or wrong password.
    """
    try:
        raw_envelope = base64.b64decode(token.encode()).decode()
        envelope = json.loads(raw_envelope)
    except Exception as exc:
        raise ValueError(f"Invalid share token format: {exc}") from exc

    version = envelope.get("version")
    if version != SHARE_FORMAT_VERSION:
        raise ValueError(
            f"Unsupported share format version: {version}. "
            f"Expected {SHARE_FORMAT_VERSION}."
        )

    blob = envelope.get("blob", "")
    try:
        decrypted = decrypt(blob, password)
    except Exception as exc:
        raise ValueError(f"Decryption failed — wrong password or corrupted token.") from exc

    try:
        payload = json.loads(decrypted)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Decrypted payload is not valid JSON: {exc}") from exc

    return payload


def merge_entries(base_entries: list, incoming_entries: list) -> list:
    """Merge incoming entries into base, skipping duplicates by label+version."""
    existing_keys = {
        (e["label"], e["version"]) for e in base_entries
    }
    merged = list(base_entries)
    for entry in incoming_entries:
        key = (entry["label"], entry["version"])
        if key not in existing_keys:
            merged.append(entry)
            existing_keys.add(key)
    return merged

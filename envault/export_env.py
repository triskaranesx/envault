"""Export decrypted vault entries to a plain .env file format."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from envault.vault import _load_vault_raw, get_entry
from envault.crypto import decrypt


def export_env(
    vault_dir: str,
    password: str,
    output_path: Optional[str] = None,
    label_filter: Optional[list[str]] = None,
) -> str:
    """Decrypt all (or selected) vault entries and render as .env content.

    Args:
        vault_dir: Path to the vault directory.
        password: Master password used to decrypt entries.
        output_path: If provided, write the .env content to this file.
        label_filter: Optional list of labels to include. None means all.

    Returns:
        The .env file content as a string.

    Raises:
        ValueError: If the vault is empty or a label is not found.
        Exception: Propagated from decrypt on bad password / corrupted data.
    """
    vault = _load_vault_raw(vault_dir)
    entries = vault.get("entries", [])

    if not entries:
        raise ValueError("Vault is empty — nothing to export.")

    labels_to_export = label_filter if label_filter else [e["label"] for e in entries]

    lines: list[str] = []
    for label in labels_to_export:
        match = next((e for e in entries if e["label"] == label), None)
        if match is None:
            raise ValueError(f"Label '{label}' not found in vault.")
        plaintext = decrypt(match["ciphertext"], password)
        # Escape newlines inside values; wrap in double quotes if needed
        safe_value = plaintext.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
        if any(ch in plaintext for ch in (" ", "\t", "#", "$", "'")):
            lines.append(f'{label}="{safe_value}"')
        else:
            lines.append(f"{label}={safe_value}")

    content = "\n".join(lines) + "\n"

    if output_path:
        Path(output_path).write_text(content, encoding="utf-8")

    return content

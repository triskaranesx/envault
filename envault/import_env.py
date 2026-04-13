"""Import .env file contents into the vault."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from envault.vault import add_entry, init_vault


_LINE_RE = re.compile(
    r'^\s*(?:export\s+)?'
    r'([A-Za-z_][A-Za-z0-9_]*)'
    r'\s*=\s*'
    r'("(?:[^"\\]|\\.)*"|\x27(?:[^\x27\\]|\\.)*\x27|[^#\r\n]*)'
    r'\s*(?:#.*)?$'
)


def _strip_quotes(value: str) -> str:
    """Remove surrounding single or double quotes from a value."""
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        value = value[1:-1]
        value = value.replace('\\"', '"').replace("\\'"', "'")
    return value


def parse_env_file(path: Path) -> list[tuple[str, str]]:
    """Parse a .env file and return a list of (key, value) pairs."""
    pairs: list[tuple[str, str]] = []
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        m = _LINE_RE.match(line)
        if m:
            key = m.group(1)
            value = _strip_quotes(m.group(2))
            pairs.append((key, value))
    return pairs


def import_env_file(
    vault_path: Path,
    env_path: Path,
    password: str,
    prefix: Optional[str] = None,
    overwrite: bool = False,
) -> dict[str, int]:
    """Import a .env file into the vault.

    Returns a summary dict with keys 'imported' and 'skipped'.
    """
    if not vault_path.exists():
        init_vault(vault_path, password)

    pairs = parse_env_file(env_path)
    imported = 0
    skipped = 0

    from envault.vault import _load_vault_raw, get_entry

    vault = _load_vault_raw(vault_path)
    existing_labels = {e["label"] for e in vault.get("entries", [])}

    for key, value in pairs:
        label = f"{prefix}.{key}" if prefix else key
        if label in existing_labels and not overwrite:
            skipped += 1
            continue
        add_entry(vault_path, label, value, password)
        existing_labels.add(label)
        imported += 1

    return {"imported": imported, "skipped": skipped}

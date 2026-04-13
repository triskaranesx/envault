"""Search and filter vault entries by label, tag, or value pattern."""

import fnmatch
from typing import List, Optional

from envault.vault import list_entries
from envault.tags import get_tags


def search_entries(
    vault_dir: str,
    password: str,
    label_pattern: Optional[str] = None,
    tag: Optional[str] = None,
    value_pattern: Optional[str] = None,
) -> List[dict]:
    """Return entries matching all provided filters.

    Filters are ANDed together — an entry must satisfy every supplied filter
    to be included in the results.

    Args:
        vault_dir: Path to the vault directory.
        password: Master password used to decrypt entry values.
        label_pattern: Unix shell-style wildcard matched against the label
            (e.g. ``"DB_*"``).  Case-insensitive.
        tag: Return only entries that carry this exact tag.
        value_pattern: Unix shell-style wildcard matched against the
            decrypted value.  Case-sensitive.

    Returns:
        A list of dicts with keys ``index``, ``label``, ``value``, and
        ``tags``.
    """
    all_entries = list_entries(vault_dir, password)
    results = []

    for entry in all_entries:
        if label_pattern is not None:
            if not fnmatch.fnmatch(entry["label"].upper(), label_pattern.upper()):
                continue

        if tag is not None:
            entry_tags = get_tags(vault_dir, entry["label"])
            if tag not in entry_tags:
                continue

        if value_pattern is not None:
            if not fnmatch.fnmatch(entry["value"], value_pattern):
                continue

        entry_tags = get_tags(vault_dir, entry["label"])
        results.append(
            {
                "index": entry["index"],
                "label": entry["label"],
                "value": entry["value"],
                "tags": entry_tags,
            }
        )

    return results

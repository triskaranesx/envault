"""Tag management for vault entries."""

import json
from pathlib import Path
from typing import List, Dict, Optional

_TAGS_FILE = ".envault_tags.json"


def _load_tags(vault_path: str) -> Dict[str, List[str]]:
    """Load tag mappings from disk. Returns dict of label -> list of tags."""
    p = Path(vault_path) / _TAGS_FILE
    if not p.exists():
        return {}
    with open(p, "r") as f:
        return json.load(f)


def _save_tags(vault_path: str, tags: Dict[str, List[str]]) -> None:
    """Persist tag mappings to disk."""
    p = Path(vault_path) / _TAGS_FILE
    with open(p, "w") as f:
        json.dump(tags, f, indent=2)


def add_tag(vault_path: str, label: str, tag: str) -> None:
    """Add a tag to a vault entry label."""
    tags = _load_tags(vault_path)
    if label not in tags:
        tags[label] = []
    if tag not in tags[label]:
        tags[label].append(tag)
    _save_tags(vault_path, tags)


def remove_tag(vault_path: str, label: str, tag: str) -> bool:
    """Remove a tag from a label. Returns True if removed, False if not found."""
    tags = _load_tags(vault_path)
    if label not in tags or tag not in tags[label]:
        return False
    tags[label].remove(tag)
    if not tags[label]:
        del tags[label]
    _save_tags(vault_path, tags)
    return True


def get_tags(vault_path: str, label: str) -> List[str]:
    """Return all tags for a given label."""
    tags = _load_tags(vault_path)
    return tags.get(label, [])


def find_by_tag(vault_path: str, tag: str) -> List[str]:
    """Return all labels that have the given tag."""
    tags = _load_tags(vault_path)
    return [label for label, label_tags in tags.items() if tag in label_tags]


def clear_tags_for_label(vault_path: str, label: str) -> None:
    """Remove all tags associated with a label."""
    tags = _load_tags(vault_path)
    if label in tags:
        del tags[label]
        _save_tags(vault_path, tags)

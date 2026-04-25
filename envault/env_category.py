"""Category management for vault entries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


CATEGORY_VALID_CHARS = set(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
)


class CategoryError(Exception):
    """Raised for invalid category operations."""


def _category_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".categories.json"


def _load_categories(vault_dir: str) -> Dict[str, str]:
    path = _category_path(vault_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_categories(vault_dir: str, data: Dict[str, str]) -> None:
    _category_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_category(vault_dir: str, label: str, category: str) -> None:
    """Assign a category to a label."""
    if not label:
        raise CategoryError("Label must not be empty.")
    if not category:
        raise CategoryError("Category must not be empty.")
    if not all(c in CATEGORY_VALID_CHARS for c in category):
        raise CategoryError(
            f"Category '{category}' contains invalid characters. "
            "Use letters, digits, underscores, or hyphens."
        )
    data = _load_categories(vault_dir)
    data[label] = category
    _save_categories(vault_dir, data)


def get_category(vault_dir: str, label: str) -> Optional[str]:
    """Return the category for a label, or None if not set."""
    return _load_categories(vault_dir).get(label)


def remove_category(vault_dir: str, label: str) -> bool:
    """Remove category for a label. Returns True if it existed."""
    data = _load_categories(vault_dir)
    if label in data:
        del data[label]
        _save_categories(vault_dir, data)
        return True
    return False


def list_categories(vault_dir: str) -> Dict[str, str]:
    """Return all label -> category mappings."""
    return dict(_load_categories(vault_dir))


def find_by_category(vault_dir: str, category: str) -> List[str]:
    """Return all labels assigned to the given category."""
    return [
        label
        for label, cat in _load_categories(vault_dir).items()
        if cat.lower() == category.lower()
    ]

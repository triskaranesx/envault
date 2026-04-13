"""Template support for envault: save and apply named sets of keys."""

import json
from pathlib import Path
from typing import Dict, List, Optional

_TEMPLATES_FILE = "templates.json"


def _load_templates(vault_dir: str) -> Dict[str, List[str]]:
    path = Path(vault_dir) / _TEMPLATES_FILE
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_templates(vault_dir: str, data: Dict[str, List[str]]) -> None:
    path = Path(vault_dir) / _TEMPLATES_FILE
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def save_template(vault_dir: str, name: str, labels: List[str]) -> None:
    """Save a named template containing the given list of entry labels."""
    if not labels:
        raise ValueError("Template must contain at least one label.")
    templates = _load_templates(vault_dir)
    templates[name] = list(labels)
    _save_templates(vault_dir, templates)


def get_template(vault_dir: str, name: str) -> Optional[List[str]]:
    """Return the list of labels for a template, or None if not found."""
    templates = _load_templates(vault_dir)
    return templates.get(name)


def delete_template(vault_dir: str, name: str) -> bool:
    """Delete a template by name. Returns True if deleted, False if not found."""
    templates = _load_templates(vault_dir)
    if name not in templates:
        return False
    del templates[name]
    _save_templates(vault_dir, templates)
    return True


def list_templates(vault_dir: str) -> Dict[str, List[str]]:
    """Return all saved templates."""
    return _load_templates(vault_dir)

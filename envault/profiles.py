"""Profile management for envault — named sets of labels for different environments."""

import json
from pathlib import Path
from typing import Dict, List, Optional


PROFILES_FILE = "profiles.json"


def _load_profiles(vault_dir: str) -> Dict[str, List[str]]:
    path = Path(vault_dir) / PROFILES_FILE
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_profiles(vault_dir: str, data: Dict[str, List[str]]) -> None:
    path = Path(vault_dir) / PROFILES_FILE
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def save_profile(vault_dir: str, name: str, labels: List[str]) -> None:
    """Save a named profile with a list of labels."""
    if not name or not name.strip():
        raise ValueError("Profile name must not be empty.")
    if not labels:
        raise ValueError("Profile must contain at least one label.")
    data = _load_profiles(vault_dir)
    data[name] = list(labels)
    _save_profiles(vault_dir, data)


def get_profile(vault_dir: str, name: str) -> Optional[List[str]]:
    """Return the list of labels for a profile, or None if not found."""
    data = _load_profiles(vault_dir)
    return data.get(name)


def delete_profile(vault_dir: str, name: str) -> bool:
    """Delete a profile by name. Returns True if it existed."""
    data = _load_profiles(vault_dir)
    if name not in data:
        return False
    del data[name]
    _save_profiles(vault_dir, data)
    return True


def list_profiles(vault_dir: str) -> List[str]:
    """Return a sorted list of all profile names."""
    data = _load_profiles(vault_dir)
    return sorted(data.keys())

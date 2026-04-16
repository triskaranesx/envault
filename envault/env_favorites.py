import json
from pathlib import Path
from typing import List


def _favorites_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".favorites.json"


def _load_favorites(vault_dir: str) -> List[str]:
    p = _favorites_path(vault_dir)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save_favorites(vault_dir: str, favorites: List[str]) -> None:
    _favorites_path(vault_dir).write_text(json.dumps(favorites, indent=2))


def add_favorite(vault_dir: str, label: str) -> None:
    if not label:
        raise ValueError("Label must not be empty")
    favs = _load_favorites(vault_dir)
    if label not in favs:
        favs.append(label)
        _save_favorites(vault_dir, favs)


def remove_favorite(vault_dir: str, label: str) -> bool:
    favs = _load_favorites(vault_dir)
    if label in favs:
        favs.remove(label)
        _save_favorites(vault_dir, favs)
        return True
    return False


def list_favorites(vault_dir: str) -> List[str]:
    return _load_favorites(vault_dir)


def is_favorite(vault_dir: str, label: str) -> bool:
    return label in _load_favorites(vault_dir)

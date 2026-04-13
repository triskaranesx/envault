"""Permission management for envault vaults.

Allows assigning read/write/admin roles to actors (users/teams)
per vault or per label.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

VALID_ROLES = {"read", "write", "admin"}
_PERMISSIONS_FILE = "permissions.json"


def _load_permissions(vault_dir: str) -> Dict:
    path = Path(vault_dir) / _PERMISSIONS_FILE
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_permissions(vault_dir: str, data: Dict) -> None:
    path = Path(vault_dir) / _PERMISSIONS_FILE
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_permission(vault_dir: str, actor: str, role: str, label: Optional[str] = None) -> None:
    """Assign a role to an actor, optionally scoped to a label."""
    if not actor or not actor.strip():
        raise ValueError("Actor name must not be empty.")
    if role not in VALID_ROLES:
        raise ValueError(f"Invalid role '{role}'. Must be one of: {sorted(VALID_ROLES)}")
    data = _load_permissions(vault_dir)
    key = f"label:{label}" if label else "vault"
    data.setdefault(key, {})
    data[key][actor] = role
    _save_permissions(vault_dir, data)


def get_permission(vault_dir: str, actor: str, label: Optional[str] = None) -> Optional[str]:
    """Get the role for an actor, optionally scoped to a label."""
    data = _load_permissions(vault_dir)
    key = f"label:{label}" if label else "vault"
    return data.get(key, {}).get(actor)


def remove_permission(vault_dir: str, actor: str, label: Optional[str] = None) -> bool:
    """Remove a permission entry. Returns True if it existed."""
    data = _load_permissions(vault_dir)
    key = f"label:{label}" if label else "vault"
    if actor in data.get(key, {}):
        del data[key][actor]
        if not data[key]:
            del data[key]
        _save_permissions(vault_dir, data)
        return True
    return False


def list_permissions(vault_dir: str, label: Optional[str] = None) -> List[Dict]:
    """List all permissions for vault or a specific label scope."""
    data = _load_permissions(vault_dir)
    key = f"label:{label}" if label else "vault"
    scope = data.get(key, {})
    return [{"actor": actor, "role": role} for actor, role in sorted(scope.items())]


def has_permission(vault_dir: str, actor: str, required_role: str, label: Optional[str] = None) -> bool:
    """Check if actor has at least the required role level."""
    role_rank = {"read": 1, "write": 2, "admin": 3}
    role = get_permission(vault_dir, actor, label) or get_permission(vault_dir, actor)
    if role is None:
        return False
    return role_rank.get(role, 0) >= role_rank.get(required_role, 99)

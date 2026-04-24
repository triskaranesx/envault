"""Dependency tracking for vault entries.

Allows defining relationships between labels so that dependent entries
can be identified when a value changes (e.g. DATABASE_URL depends on
DB_HOST and DB_PORT).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Set


class DependencyError(Exception):
    """Raised when a dependency operation is invalid."""


def _deps_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".envault_deps.json"


def _load_deps(vault_dir: str) -> Dict[str, List[str]]:
    """Load the dependency map from disk.  Returns {} if absent."""
    path = _deps_path(vault_dir)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save_deps(vault_dir: str, deps: Dict[str, List[str]]) -> None:
    """Persist the dependency map to disk."""
    _deps_path(vault_dir).write_text(json.dumps(deps, indent=2))


def add_dependency(vault_dir: str, label: str, depends_on: str) -> None:
    """Record that *label* depends on *depends_on*.

    Raises DependencyError if either label is empty or if adding the
    dependency would create a direct self-loop.
    """
    if not label or not label.strip():
        raise DependencyError("label must not be empty")
    if not depends_on or not depends_on.strip():
        raise DependencyError("depends_on must not be empty")
    if label == depends_on:
        raise DependencyError(f"'{label}' cannot depend on itself")

    deps = _load_deps(vault_dir)
    existing: List[str] = deps.get(label, [])
    if depends_on not in existing:
        existing.append(depends_on)
    deps[label] = existing
    _save_deps(vault_dir, deps)


def remove_dependency(vault_dir: str, label: str, depends_on: str) -> bool:
    """Remove the dependency of *label* on *depends_on*.

    Returns True if the dependency existed and was removed, False otherwise.
    """
    deps = _load_deps(vault_dir)
    existing: List[str] = deps.get(label, [])
    if depends_on not in existing:
        return False
    existing.remove(depends_on)
    if existing:
        deps[label] = existing
    else:
        deps.pop(label, None)
    _save_deps(vault_dir, deps)
    return True


def get_dependencies(vault_dir: str, label: str) -> List[str]:
    """Return the list of labels that *label* directly depends on."""
    deps = _load_deps(vault_dir)
    return list(deps.get(label, []))


def get_dependents(vault_dir: str, label: str) -> List[str]:
    """Return all labels that directly depend on *label*."""
    deps = _load_deps(vault_dir)
    return [lbl for lbl, parents in deps.items() if label in parents]


def all_dependencies(vault_dir: str, label: str) -> List[str]:
    """Return the transitive closure of dependencies for *label*.

    Uses iterative BFS to avoid recursion limits on deep graphs.
    Cycles are silently ignored (the traversal stops when a node has
    already been visited).
    """
    deps = _load_deps(vault_dir)
    visited: Set[str] = set()
    queue: List[str] = list(deps.get(label, []))
    result: List[str] = []

    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)
        result.append(current)
        queue.extend(deps.get(current, []))

    return result


def clear_dependencies(vault_dir: str, label: str) -> None:
    """Remove all dependency records where *label* is the dependent."""
    deps = _load_deps(vault_dir)
    deps.pop(label, None)
    _save_deps(vault_dir, deps)


def list_all_dependencies(vault_dir: str) -> Dict[str, List[str]]:
    """Return the full dependency map as a plain dict."""
    return _load_deps(vault_dir)

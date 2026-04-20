"""Dependency tracking between vault entries.

Allows users to declare that one label depends on another,
enabling impact analysis when values change.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set


class DependencyError(Exception):
    """Raised when a dependency operation fails."""


def _deps_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".envault_dependencies.json"


def _load_deps(vault_dir: str) -> Dict[str, List[str]]:
    """Load the dependency map from disk.

    Returns a dict mapping each label to a list of labels it depends on.
    """
    path = _deps_path(vault_dir)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_deps(vault_dir: str, deps: Dict[str, List[str]]) -> None:
    """Persist the dependency map to disk."""
    path = _deps_path(vault_dir)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(deps, fh, indent=2)


def add_dependency(vault_dir: str, label: str, depends_on: str) -> None:
    """Declare that *label* depends on *depends_on*.

    Args:
        vault_dir: Path to the vault directory.
        label: The label that has a dependency.
        depends_on: The label that *label* relies on.

    Raises:
        DependencyError: If either label is empty, or if the dependency
            would create a cycle.
    """
    if not label or not label.strip():
        raise DependencyError("label must not be empty")
    if not depends_on or not depends_on.strip():
        raise DependencyError("depends_on must not be empty")
    if label == depends_on:
        raise DependencyError("a label cannot depend on itself")

    deps = _load_deps(vault_dir)

    # Cycle detection: would adding label -> depends_on create a cycle?
    if _would_create_cycle(deps, label, depends_on):
        raise DependencyError(
            f"adding '{label} -> {depends_on}' would create a dependency cycle"
        )

    deps.setdefault(label, [])
    if depends_on not in deps[label]:
        deps[label].append(depends_on)

    _save_deps(vault_dir, deps)


def remove_dependency(vault_dir: str, label: str, depends_on: str) -> bool:
    """Remove a declared dependency.

    Returns True if the dependency existed and was removed, False otherwise.
    """
    deps = _load_deps(vault_dir)
    if label not in deps or depends_on not in deps[label]:
        return False
    deps[label].remove(depends_on)
    if not deps[label]:
        del deps[label]
    _save_deps(vault_dir, deps)
    return True


def get_dependencies(vault_dir: str, label: str) -> List[str]:
    """Return the list of labels that *label* directly depends on."""
    deps = _load_deps(vault_dir)
    return list(deps.get(label, []))


def get_dependents(vault_dir: str, label: str) -> List[str]:
    """Return all labels that directly depend on *label*."""
    deps = _load_deps(vault_dir)
    return [lbl for lbl, targets in deps.items() if label in targets]


def get_all_dependencies(vault_dir: str, label: str) -> List[str]:
    """Return the transitive closure of labels that *label* depends on."""
    deps = _load_deps(vault_dir)
    visited: Set[str] = set()
    stack = list(deps.get(label, []))
    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)
        stack.extend(deps.get(current, []))
    return sorted(visited)


def list_all_dependencies(vault_dir: str) -> Dict[str, List[str]]:
    """Return the full dependency map."""
    return _load_deps(vault_dir)


def _would_create_cycle(
    deps: Dict[str, List[str]], label: str, new_dep: str
) -> bool:
    """Return True if adding label -> new_dep would introduce a cycle."""
    # BFS/DFS from new_dep; if we can reach label, it's a cycle.
    visited: Set[str] = set()
    stack = [new_dep]
    while stack:
        current = stack.pop()
        if current == label:
            return True
        if current in visited:
            continue
        visited.add(current)
        stack.extend(deps.get(current, []))
    return False

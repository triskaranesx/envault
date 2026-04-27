"""Track the source/origin metadata for vault entries."""

import json
from pathlib import Path
from typing import Optional, Dict, Any


SOURCES_FILE = ".envault_sources.json"

VALID_SOURCE_TYPES = {"manual", "import", "generated", "sync", "migration"}


class SourceError(ValueError):
    pass


def _sources_path(vault_dir: str) -> Path:
    return Path(vault_dir) / SOURCES_FILE


def _load_sources(vault_dir: str) -> Dict[str, Any]:
    p = _sources_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_sources(vault_dir: str, data: Dict[str, Any]) -> None:
    _sources_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_source(vault_dir: str, label: str, source_type: str, origin: Optional[str] = None) -> Dict[str, Any]:
    """Set the source metadata for a label."""
    if not label or not label.strip():
        raise SourceError("Label must not be empty.")
    if source_type not in VALID_SOURCE_TYPES:
        raise SourceError(
            f"Invalid source type '{source_type}'. Must be one of: {sorted(VALID_SOURCE_TYPES)}"
        )
    data = _load_sources(vault_dir)
    record = {"type": source_type}
    if origin is not None:
        record["origin"] = origin
    data[label] = record
    _save_sources(vault_dir, data)
    return record


def get_source(vault_dir: str, label: str) -> Optional[Dict[str, Any]]:
    """Return source metadata for a label, or None if not set."""
    return _load_sources(vault_dir).get(label)


def remove_source(vault_dir: str, label: str) -> bool:
    """Remove source metadata for a label. Returns True if removed."""
    data = _load_sources(vault_dir)
    if label not in data:
        return False
    del data[label]
    _save_sources(vault_dir, data)
    return True


def list_sources(vault_dir: str) -> Dict[str, Any]:
    """Return all source records."""
    return dict(_load_sources(vault_dir))


def filter_by_source_type(vault_dir: str, source_type: str) -> Dict[str, Any]:
    """Return all labels with a given source type."""
    return {
        label: record
        for label, record in _load_sources(vault_dir).items()
        if record.get("type") == source_type
    }

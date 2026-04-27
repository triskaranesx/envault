"""CLI commands for managing entry source/origin metadata."""

import click
from envault.env_source import (
    set_source,
    get_source,
    remove_source,
    list_sources,
    filter_by_source_type,
    VALID_SOURCE_TYPES,
    SourceError,
)


@click.group("source")
def cmd_source():
    """Manage source/origin metadata for vault entries."""


@cmd_source.command("set")
@click.argument("label")
@click.argument("source_type", metavar="TYPE")
@click.option("--origin", default=None, help="Optional origin string (e.g. filename or URL).")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def cmd_source_set(label, source_type, origin, vault):
    """Set the source TYPE for LABEL."""
    try:
        record = set_source(vault, label, source_type, origin=origin)
        click.echo(f"Source set: {label} -> {record}")
    except SourceError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cmd_source.command("get")
@click.argument("label")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def cmd_source_get(label, vault):
    """Get the source metadata for LABEL."""
    record = get_source(vault, label)
    if record is None:
        click.echo(f"No source set for '{label}'.")
    else:
        origin_part = f", origin={record['origin']}" if "origin" in record else ""
        click.echo(f"{label}: type={record['type']}{origin_part}")


@cmd_source.command("remove")
@click.argument("label")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def cmd_source_remove(label, vault):
    """Remove source metadata for LABEL."""
    removed = remove_source(vault, label)
    if removed:
        click.echo(f"Source removed for '{label}'.")
    else:
        click.echo(f"No source record found for '{label}'.")


@cmd_source.command("list")
@click.option("--type", "source_type", default=None, help="Filter by source type.")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def cmd_source_list(source_type, vault):
    """List all source records, optionally filtered by TYPE."""
    if source_type:
        records = filter_by_source_type(vault, source_type)
    else:
        records = list_sources(vault)
    if not records:
        click.echo("No source records found.")
        return
    for label, record in sorted(records.items()):
        origin_part = f"  origin={record['origin']}" if "origin" in record else ""
        click.echo(f"  {label}: {record['type']}{origin_part}")

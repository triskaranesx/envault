"""CLI commands for snapshot management."""

import click
from envault.snapshots import (
    save_snapshot,
    get_snapshot,
    list_snapshots,
    restore_snapshot,
    delete_snapshot,
)


@click.group("snapshot")
def cmd_snapshot():
    """Manage named vault snapshots."""


@cmd_snapshot.command("save")
@click.argument("name")
@click.option("--vault-dir", default=".", show_default=True, help="Path to vault directory.")
def cmd_snapshot_save(name, vault_dir):
    """Save current vault state as a named snapshot."""
    try:
        ts = save_snapshot(vault_dir, name)
        click.echo(f"Snapshot '{name}' saved at {ts}.")
    except (ValueError, FileNotFoundError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cmd_snapshot.command("show")
@click.argument("name")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_snapshot_show(name, vault_dir):
    """Show metadata for a named snapshot."""
    snap = get_snapshot(vault_dir, name)
    if snap is None:
        click.echo(f"Snapshot '{name}' not found.", err=True)
        raise SystemExit(1)
    entry_count = len(snap["vault"].get("entries", []))
    click.echo(f"Name:      {name}")
    click.echo(f"Created:   {snap['created_at']}")
    click.echo(f"Entries:   {entry_count}")


@cmd_snapshot.command("list")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_snapshot_list(vault_dir):
    """List all saved snapshots."""
    snaps = list_snapshots(vault_dir)
    if not snaps:
        click.echo("No snapshots found.")
        return
    for s in snaps:
        click.echo(f"{s['name']:30s}  {s['created_at']}")


@cmd_snapshot.command("restore")
@click.argument("name")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_snapshot_restore(name, vault_dir):
    """Restore vault from a named snapshot."""
    try:
        count = restore_snapshot(vault_dir, name)
        click.echo(f"Restored snapshot '{name}' ({count} entries).")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cmd_snapshot.command("delete")
@click.argument("name")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_snapshot_delete(name, vault_dir):
    """Delete a named snapshot."""
    deleted = delete_snapshot(vault_dir, name)
    if deleted:
        click.echo(f"Snapshot '{name}' deleted.")
    else:
        click.echo(f"Snapshot '{name}' not found.", err=True)
        raise SystemExit(1)

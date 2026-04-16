"""CLI commands for bookmark management."""
import click
from envault.env_bookmarks import (
    add_bookmark, remove_bookmark, get_bookmark,
    list_bookmarks, is_bookmarked,
)


@click.group("bookmark")
def cmd_bookmark():
    """Manage bookmarked vault entries."""


@cmd_bookmark.command("add")
@click.argument("label")
@click.option("--note", default="", help="Optional note for the bookmark.")
@click.option("--vault", default=".", help="Vault directory.")
def cmd_bm_add(label, note, vault):
    """Bookmark a label."""
    add_bookmark(vault, label, note)
    click.echo(f"Bookmarked '{label}'.")


@cmd_bookmark.command("remove")
@click.argument("label")
@click.option("--vault", default=".", help="Vault directory.")
def cmd_bm_remove(label, vault):
    """Remove a bookmark."""
    removed = remove_bookmark(vault, label)
    if removed:
        click.echo(f"Removed bookmark '{label}'.")
    else:
        click.echo(f"No bookmark found for '{label}'.")
        raise SystemExit(1)


@cmd_bookmark.command("get")
@click.argument("label")
@click.option("--vault", default=".", help="Vault directory.")
def cmd_bm_get(label, vault):
    """Show a bookmark."""
    bm = get_bookmark(vault, label)
    if bm is None:
        click.echo(f"No bookmark for '{label}'.")
        raise SystemExit(1)
    note = bm.get("note") or "(no note)"
    click.echo(f"{label}: {note}")


@cmd_bookmark.command("list")
@click.option("--vault", default=".", help="Vault directory.")
def cmd_bm_list(vault):
    """List all bookmarks."""
    bms = list_bookmarks(vault)
    if not bms:
        click.echo("No bookmarks.")
        return
    for label, meta in bms.items():
        note = meta.get("note") or "(no note)"
        click.echo(f"  {label}: {note}")


@cmd_bookmark.command("check")
@click.argument("label")
@click.option("--vault", default=".", help="Vault directory.")
def cmd_bm_check(label, vault):
    """Check if a label is bookmarked."""
    if is_bookmarked(vault, label):
        click.echo(f"'{label}' is bookmarked.")
    else:
        click.echo(f"'{label}' is not bookmarked.")

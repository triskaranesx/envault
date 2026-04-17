"""CLI commands for archiving and restoring vault entries."""
import click
from envault.vault import get_entry, add_entry, list_entries, _load_vault_raw, _save_vault_raw
from envault import env_archive as arc


@click.group("archive")
def cmd_archive():
    """Archive (soft-delete) and restore vault entries."""


@cmd_archive.command("add")
@click.argument("label")
@click.option("--vault", default=".", show_default=True)
def cmd_archive_add(label, vault):
    """Archive an entry (soft-delete it from the vault)."""
    raw = _load_vault_raw(vault)
    entries = raw.get("entries", [])
    match = next((e for e in entries if e["label"] == label), None)
    if match is None:
        click.echo(f"Error: label '{label}' not found.", err=True)
        raise SystemExit(1)
    arc.archive_entry(vault, label, match)
    raw["entries"] = [e for e in entries if e["label"] != label]
    _save_vault_raw(vault, raw)
    click.echo(f"Archived '{label}'.")


@cmd_archive.command("restore")
@click.argument("label")
@click.option("--vault", default=".", show_default=True)
def cmd_archive_restore(label, vault):
    """Restore an archived entry back into the vault."""
    try:
        entry = arc.restore_entry(vault, label)
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    raw = _load_vault_raw(vault)
    raw.setdefault("entries", []).append(entry)
    _save_vault_raw(vault, raw)
    click.echo(f"Restored '{label}' to vault.")


@cmd_archive.command("list")
@click.option("--vault", default=".", show_default=True)
def cmd_archive_list(vault):
    """List all archived entry labels."""
    labels = arc.list_archived(vault)
    if not labels:
        click.echo("No archived entries.")
    else:
        for lbl in labels:
            click.echo(lbl)


@cmd_archive.command("purge")
@click.argument("label")
@click.option("--vault", default=".", show_default=True)
def cmd_archive_purge(label, vault):
    """Permanently delete an archived entry."""
    removed = arc.purge_archived(vault, label)
    if removed:
        click.echo(f"Purged '{label}' permanently.")
    else:
        click.echo(f"No archived entry '{label}' found.", err=True)
        raise SystemExit(1)

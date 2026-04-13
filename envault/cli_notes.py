"""CLI commands for managing per-entry notes."""

from __future__ import annotations

import click

from envault.notes import get_note, list_notes, remove_note, set_note


@click.group("notes")
def cmd_notes() -> None:
    """Manage plaintext notes attached to vault entries."""


@cmd_notes.command("set")
@click.argument("label")
@click.argument("note")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def cmd_note_set(label: str, note: str, vault: str) -> None:
    """Attach NOTE to the entry identified by LABEL."""
    try:
        set_note(vault, label, note)
        click.echo(f"Note set for '{label}'.")
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


@cmd_notes.command("get")
@click.argument("label")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def cmd_note_get(label: str, vault: str) -> None:
    """Print the note attached to LABEL."""
    note = get_note(vault, label)
    if note is None:
        click.echo(f"No note found for '{label}'.")
    else:
        click.echo(note)


@cmd_notes.command("remove")
@click.argument("label")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def cmd_note_remove(label: str, vault: str) -> None:
    """Remove the note attached to LABEL."""
    removed = remove_note(vault, label)
    if removed:
        click.echo(f"Note removed for '{label}'.")
    else:
        click.echo(f"No note to remove for '{label}'.")


@cmd_notes.command("list")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def cmd_note_list(vault: str) -> None:
    """List all entries that have notes."""
    notes = list_notes(vault)
    if not notes:
        click.echo("No notes stored.")
        return
    for label, note in sorted(notes.items()):
        click.echo(f"{label}: {note}")

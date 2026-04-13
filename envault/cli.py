"""Main CLI entry point for envault."""

from __future__ import annotations

import click

from envault.vault import init_vault, add_entry, get_entry, list_entries
from envault.cli_share import cmd_export, cmd_import
from envault.cli_history import cmd_log, cmd_clear_log
from envault.cli_audit import cmd_audit, cmd_clear_audit
from envault.cli_tags import cmd_tags
from envault.cli_rotation import cmd_rotate
from envault.cli_search import cmd_search
from envault.cli_diff import cmd_diff


@click.group()
def cli() -> None:
    """envault — encrypt and version your .env secrets."""


@cli.command("init")
@click.option("--vault", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
def cmd_init(vault: str, password: str) -> None:
    """Initialise a new vault."""
    init_vault(vault, password)
    click.echo(f"Vault initialised at {vault}")


@cli.command("add")
@click.argument("label")
@click.argument("value")
@click.option("--vault", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def cmd_add(label: str, value: str, vault: str, password: str) -> None:
    """Add or update a secret."""
    idx = add_entry(vault, label, value, password)
    click.echo(f"Stored '{label}' as entry #{idx}")


@cli.command("get")
@click.argument("label")
@click.option("--vault", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def cmd_get(label: str, vault: str, password: str) -> None:
    """Retrieve a secret by label."""
    value = get_entry(vault, label, password)
    if value is None:
        click.echo(f"No entry found for '{label}'")
    else:
        click.echo(value)


@cli.command("list")
@click.option("--vault", default=".envault", show_default=True)
def cmd_list(vault: str) -> None:
    """List all secret labels."""
    labels = list_entries(vault)
    if not labels:
        click.echo("No entries.")
    for lbl in labels:
        click.echo(lbl)


# Register sub-command groups
cli.add_command(cmd_export, name="export")
cli.add_command(cmd_import, name="import")
cli.add_command(cmd_log, name="log")
cli.add_command(cmd_clear_log, name="clear-log")
cli.add_command(cmd_audit, name="audit")
cli.add_command(cmd_clear_audit, name="clear-audit")
cli.add_command(cmd_tags, name="tags")
cli.add_command(cmd_rotate, name="rotate")
cli.add_command(cmd_search, name="search")
cli.add_command(cmd_diff, name="diff")


if __name__ == "__main__":
    cli()

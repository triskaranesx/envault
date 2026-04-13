"""Main CLI entry-point for envault."""

from __future__ import annotations

from pathlib import Path

import click

from envault.vault import init_vault, add_entry, get_entry, list_entries
from envault.cli_share import cmd_export, cmd_import
from envault.cli_history import cmd_log, cmd_clear_log
from envault.cli_audit import cmd_audit, cmd_clear_audit
from envault.cli_tags import cmd_tags
from envault.cli_rotation import cmd_rotate


@click.group()
def cli() -> None:
    """envault — encrypted .env vault with team-sharing support."""


@cli.command("init")
@click.option("--vault", default=".envault", show_default=True)
def cmd_init(vault: str) -> None:
    """Initialise a new vault."""
    vault_path = Path(vault)
    if vault_path.exists():
        raise click.ClickException(f"Vault already exists: {vault}")
    init_vault(vault_path)
    click.echo(f"Vault initialised at {vault_path}.")


@cli.command("add")
@click.argument("label")
@click.argument("value")
@click.option("--vault", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def cmd_add(label: str, value: str, vault: str, password: str) -> None:
    """Add or update a secret."""
    vault_path = Path(vault)
    if not vault_path.exists():
        raise click.ClickException(f"Vault not found: {vault}")
    add_entry(vault_path, label, value, password)
    click.echo(f"Stored '{label}'.")


@cli.command("get")
@click.argument("label")
@click.option("--vault", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def cmd_get(label: str, vault: str, password: str) -> None:
    """Retrieve a secret by label."""
    vault_path = Path(vault)
    if not vault_path.exists():
        raise click.ClickException(f"Vault not found: {vault}")
    try:
        value = get_entry(vault_path, label, password)
        click.echo(value)
    except KeyError:
        raise click.ClickException(f"Label '{label}' not found.")
    except ValueError as exc:
        raise click.ClickException(str(exc))


@cli.command("list")
@click.option("--vault", default=".envault", show_default=True)
def cmd_list(vault: str) -> None:
    """List all entry labels."""
    vault_path = Path(vault)
    if not vault_path.exists():
        raise click.ClickException(f"Vault not found: {vault}")
    labels = list_entries(vault_path)
    if not labels:
        click.echo("No entries.")
    else:
        for label in labels:
            click.echo(label)


# Register sub-command groups
cli.add_command(cmd_export, "export")
cli.add_command(cmd_import, "import")
cli.add_command(cmd_log, "log")
cli.add_command(cmd_clear_log, "clear-log")
cli.add_command(cmd_audit, "audit")
cli.add_command(cmd_clear_audit, "clear-audit")
cli.add_command(cmd_tags, "tags")
cli.add_command(cmd_rotate, "rotate")

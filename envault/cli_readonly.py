"""CLI commands for managing read-only entry flags."""

import click
from envault.env_readonly import mark_readonly, unmark_readonly, is_readonly, list_readonly


@click.group(name="readonly")
def cmd_readonly():
    """Manage read-only flags for vault entries."""


@cmd_readonly.command(name="set")
@click.argument("label")
@click.option("--vault", default=".", show_default=True, help="Vault directory")
def cmd_readonly_set(label, vault):
    """Mark an entry as read-only."""
    mark_readonly(vault, label)
    click.echo(f"Entry '{label}' marked as read-only.")


@cmd_readonly.command(name="unset")
@click.argument("label")
@click.option("--vault", default=".", show_default=True, help="Vault directory")
def cmd_readonly_unset(label, vault):
    """Remove read-only flag from an entry."""
    unmark_readonly(vault, label)
    click.echo(f"Entry '{label}' is now writable.")


@cmd_readonly.command(name="check")
@click.argument("label")
@click.option("--vault", default=".", show_default=True, help="Vault directory")
def cmd_readonly_check(label, vault):
    """Check if an entry is read-only."""
    if is_readonly(vault, label):
        click.echo(f"'{label}' is read-only.")
    else:
        click.echo(f"'{label}' is writable.")


@cmd_readonly.command(name="list")
@click.option("--vault", default=".", show_default=True, help="Vault directory")
def cmd_readonly_list(vault):
    """List all read-only entries."""
    entries = list_readonly(vault)
    if not entries:
        click.echo("No read-only entries.")
    else:
        for label in entries:
            click.echo(label)

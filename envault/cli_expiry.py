"""CLI commands for managing entry expiry."""

import click
from envault.expiry import (
    set_expiry,
    get_expiry,
    remove_expiry,
    is_expired,
    list_expired,
    list_all_expiry,
)


@click.group("expiry")
def cmd_expiry():
    """Manage entry expiry / TTL."""


@cmd_expiry.command("set")
@click.argument("label")
@click.argument("days", type=int)
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def cmd_expiry_set(label: str, days: int, vault: str):
    """Set expiry for LABEL to DAYS days from now."""
    iso = set_expiry(vault, label, days)
    click.echo(f"Expiry set for '{label}': {iso}")


@cmd_expiry.command("get")
@click.argument("label")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def cmd_expiry_get(label: str, vault: str):
    """Show expiry date for LABEL."""
    iso = get_expiry(vault, label)
    if iso is None:
        click.echo(f"No expiry set for '{label}'.")
    else:
        expired = is_expired(vault, label)
        status = " [EXPIRED]" if expired else ""
        click.echo(f"{label}: {iso}{status}")


@cmd_expiry.command("remove")
@click.argument("label")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def cmd_expiry_remove(label: str, vault: str):
    """Remove expiry for LABEL."""
    removed = remove_expiry(vault, label)
    if removed:
        click.echo(f"Expiry removed for '{label}'.")
    else:
        click.echo(f"No expiry was set for '{label}'.")


@cmd_expiry.command("list")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
@click.option("--expired-only", is_flag=True, help="Show only expired entries.")
def cmd_expiry_list(vault: str, expired_only: bool):
    """List expiry dates for all entries."""
    if expired_only:
        labels = list_expired(vault)
        if not labels:
            click.echo("No expired entries.")
        else:
            click.echo("Expired entries:")
            for label in labels:
                click.echo(f"  {label}")
    else:
        data = list_all_expiry(vault)
        if not data:
            click.echo("No expiry dates set.")
        else:
            for label, iso in sorted(data.items()):
                expired = is_expired(vault, label)
                status = " [EXPIRED]" if expired else ""
                click.echo(f"  {label}: {iso}{status}")

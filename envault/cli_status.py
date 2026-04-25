"""CLI commands for entry status management."""

import click
from envault.env_status import (
    set_status,
    get_status,
    remove_status,
    list_statuses,
    find_by_status,
    StatusError,
    VALID_STATUSES,
)


@click.group("status")
def cmd_status():
    """Manage entry status (active, deprecated, experimental, stable)."""


@cmd_status.command("set")
@click.argument("label")
@click.argument("status", type=click.Choice(sorted(VALID_STATUSES), case_sensitive=False))
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def cmd_status_set(label, status, vault):
    """Set the status for a label."""
    try:
        result = set_status(vault, label, status)
        click.echo(f"Status for '{label}' set to '{result}'.")
    except StatusError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cmd_status.command("get")
@click.argument("label")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def cmd_status_get(label, vault):
    """Get the status for a label."""
    s = get_status(vault, label)
    if s is None:
        click.echo(f"No status set for '{label}'.")
    else:
        click.echo(s)


@cmd_status.command("remove")
@click.argument("label")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def cmd_status_remove(label, vault):
    """Remove the status for a label."""
    removed = remove_status(vault, label)
    if removed:
        click.echo(f"Status for '{label}' removed.")
    else:
        click.echo(f"No status found for '{label}'.")


@cmd_status.command("list")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def cmd_status_list(vault):
    """List all label statuses."""
    data = list_statuses(vault)
    if not data:
        click.echo("No statuses set.")
        return
    for label, s in sorted(data.items()):
        click.echo(f"  {label}: {s}")


@cmd_status.command("find")
@click.argument("status", type=click.Choice(sorted(VALID_STATUSES), case_sensitive=False))
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def cmd_status_find(status, vault):
    """Find all labels with a given status."""
    labels = find_by_status(vault, status)
    if not labels:
        click.echo(f"No labels with status '{status}'.")
        return
    for label in sorted(labels):
        click.echo(f"  {label}")

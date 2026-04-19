"""CLI commands for entry priority management."""
import click
from envault.env_priority import (
    set_priority, get_priority, remove_priority,
    list_priorities, find_by_priority, VALID_PRIORITIES,
)


@click.group("priority")
def cmd_priority():
    """Manage entry priority levels."""


@cmd_priority.command("set")
@click.argument("label")
@click.argument("priority", type=click.Choice(VALID_PRIORITIES))
@click.option("--vault", default=".", show_default=True)
def cmd_priority_set(label, priority, vault):
    """Set priority for a label."""
    set_priority(vault, label, priority)
    click.echo(f"Priority for '{label}' set to '{priority}'.")


@cmd_priority.command("get")
@click.argument("label")
@click.option("--vault", default=".", show_default=True)
def cmd_priority_get(label, vault):
    """Get priority for a label."""
    p = get_priority(vault, label)
    if p is None:
        click.echo(f"No priority set for '{label}'.")
    else:
        click.echo(p)


@cmd_priority.command("remove")
@click.argument("label")
@click.option("--vault", default=".", show_default=True)
def cmd_priority_remove(label, vault):
    """Remove priority for a label."""
    removed = remove_priority(vault, label)
    if removed:
        click.echo(f"Priority removed for '{label}'.")
    else:
        click.echo(f"No priority found for '{label}'.")


@cmd_priority.command("list")
@click.option("--vault", default=".", show_default=True)
def cmd_priority_list(vault):
    """List all priorities."""
    entries = list_priorities(vault)
    if not entries:
        click.echo("No priorities set.")
    else:
        for e in entries:
            click.echo(f"{e['label']}: {e['priority']}")


@cmd_priority.command("find")
@click.argument("priority", type=click.Choice(VALID_PRIORITIES))
@click.option("--vault", default=".", show_default=True)
def cmd_priority_find(priority, vault):
    """Find labels with a given priority."""
    labels = find_by_priority(vault, priority)
    if not labels:
        click.echo(f"No labels with priority '{priority}'.")
    else:
        for label in labels:
            click.echo(label)

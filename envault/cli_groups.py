"""CLI commands for group management."""
import click
from envault.env_groups import (
    create_group, delete_group, add_label_to_group,
    remove_label_from_group, get_group, list_groups, find_groups_for_label,
)


@click.group("group")
def cmd_group():
    """Manage label groups."""


@cmd_group.command("create")
@click.argument("group")
@click.option("--vault", default=".", show_default=True)
def cmd_group_create(group, vault):
    """Create a new empty group."""
    create_group(vault, group)
    click.echo(f"Group '{group}' created.")


@cmd_group.command("delete")
@click.argument("group")
@click.option("--vault", default=".", show_default=True)
def cmd_group_delete(group, vault):
    """Delete a group."""
    delete_group(vault, group)
    click.echo(f"Group '{group}' deleted.")


@cmd_group.command("add")
@click.argument("group")
@click.argument("label")
@click.option("--vault", default=".", show_default=True)
def cmd_group_add(group, label, vault):
    """Add a label to a group."""
    add_label_to_group(vault, group, label)
    click.echo(f"Added '{label}' to group '{group}'.")


@cmd_group.command("remove")
@click.argument("group")
@click.argument("label")
@click.option("--vault", default=".", show_default=True)
def cmd_group_remove(group, label, vault):
    """Remove a label from a group."""
    remove_label_from_group(vault, group, label)
    click.echo(f"Removed '{label}' from group '{group}'.")


@cmd_group.command("show")
@click.argument("group")
@click.option("--vault", default=".", show_default=True)
def cmd_group_show(group, vault):
    """Show members of a group."""
    members = get_group(vault, group)
    if members is None:
        click.echo(f"Group '{group}' does not exist.", err=True)
        raise SystemExit(1)
    if not members:
        click.echo(f"Group '{group}' is empty.")
    else:
        for m in members:
            click.echo(m)


@cmd_group.command("list")
@click.option("--vault", default=".", show_default=True)
def cmd_group_list(vault):
    """List all groups."""
    groups = list_groups(vault)
    if not groups:
        click.echo("No groups defined.")
    else:
        for g in groups:
            click.echo(g)


@cmd_group.command("find")
@click.argument("label")
@click.option("--vault", default=".", show_default=True)
def cmd_group_find(label, vault):
    """Find all groups containing a label."""
    groups = find_groups_for_label(vault, label)
    if not groups:
        click.echo(f"'{label}' is not in any group.")
    else:
        for g in groups:
            click.echo(g)

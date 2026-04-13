"""CLI commands for tag management."""

import click
from envault.tags import add_tag, remove_tag, get_tags, find_by_tag, clear_tags_for_label


@click.group("tags")
def cmd_tags():
    """Manage tags on vault entries."""
    pass


@cmd_tags.command("add")
@click.argument("label")
@click.argument("tag")
@click.option("--vault", default=".", show_default=True, help="Path to vault directory.")
def cmd_tag_add(label: str, tag: str, vault: str):
    """Add TAG to the entry identified by LABEL."""
    add_tag(vault, label, tag)
    click.echo(f"Tag '{tag}' added to '{label}'.")


@cmd_tags.command("remove")
@click.argument("label")
@click.argument("tag")
@click.option("--vault", default=".", show_default=True, help="Path to vault directory.")
def cmd_tag_remove(label: str, tag: str, vault: str):
    """Remove TAG from the entry identified by LABEL."""
    removed = remove_tag(vault, label, tag)
    if removed:
        click.echo(f"Tag '{tag}' removed from '{label}'.")
    else:
        click.echo(f"Tag '{tag}' not found on '{label}'.")


@cmd_tags.command("list")
@click.argument("label")
@click.option("--vault", default=".", show_default=True, help="Path to vault directory.")
def cmd_tag_list(label: str, vault: str):
    """List all tags for the entry identified by LABEL."""
    tags = get_tags(vault, label)
    if not tags:
        click.echo(f"No tags found for '{label}'.")
    else:
        for tag in tags:
            click.echo(f"  - {tag}")


@cmd_tags.command("find")
@click.argument("tag")
@click.option("--vault", default=".", show_default=True, help="Path to vault directory.")
def cmd_tag_find(tag: str, vault: str):
    """Find all entries that have TAG."""
    labels = find_by_tag(vault, tag)
    if not labels:
        click.echo(f"No entries found with tag '{tag}'.")
    else:
        click.echo(f"Entries tagged '{tag}':")
        for label in labels:
            click.echo(f"  - {label}")


@cmd_tags.command("clear")
@click.argument("label")
@click.option("--vault", default=".", show_default=True, help="Path to vault directory.")
def cmd_tag_clear(label: str, vault: str):
    """Clear all tags from the entry identified by LABEL."""
    clear_tags_for_label(vault, label)
    click.echo(f"All tags cleared from '{label}'.")

"""CLI commands for category management."""

from __future__ import annotations

import click

from envault.env_category import (
    CategoryError,
    find_by_category,
    get_category,
    list_categories,
    remove_category,
    set_category,
)


@click.group("category")
def cmd_category():
    """Manage entry categories."""


@cmd_category.command("set")
@click.argument("label")
@click.argument("category")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def cmd_category_set(label: str, category: str, vault: str):
    """Assign CATEGORY to LABEL."""
    try:
        set_category(vault, label, category)
        click.echo(f"Category '{category}' set for '{label}'.")
    except CategoryError as exc:
        raise click.ClickException(str(exc))


@cmd_category.command("get")
@click.argument("label")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def cmd_category_get(label: str, vault: str):
    """Show the category assigned to LABEL."""
    cat = get_category(vault, label)
    if cat is None:
        click.echo(f"No category set for '{label}'.")
    else:
        click.echo(cat)


@cmd_category.command("remove")
@click.argument("label")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def cmd_category_remove(label: str, vault: str):
    """Remove the category from LABEL."""
    removed = remove_category(vault, label)
    if removed:
        click.echo(f"Category removed from '{label}'.")
    else:
        click.echo(f"No category was set for '{label}'.")


@cmd_category.command("list")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def cmd_category_list(vault: str):
    """List all label-to-category assignments."""
    cats = list_categories(vault)
    if not cats:
        click.echo("No categories assigned.")
        return
    for label, cat in sorted(cats.items()):
        click.echo(f"{label}: {cat}")


@cmd_category.command("find")
@click.argument("category")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def cmd_category_find(category: str, vault: str):
    """Find all labels assigned to CATEGORY."""
    labels = find_by_category(vault, category)
    if not labels:
        click.echo(f"No labels found in category '{category}'.")
        return
    for label in sorted(labels):
        click.echo(label)

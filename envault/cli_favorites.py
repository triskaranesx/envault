import click
from envault.env_favorites import add_favorite, remove_favorite, list_favorites, is_favorite


@click.group("favorites")
def cmd_favorites():
    """Manage favorite entries."""


@cmd_favorites.command("add")
@click.argument("label")
@click.option("--vault", default=".", show_default=True)
def cmd_fav_add(label, vault):
    """Mark a label as favorite."""
    try:
        add_favorite(vault, label)
        click.echo(f"Added '{label}' to favorites.")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cmd_favorites.command("remove")
@click.argument("label")
@click.option("--vault", default=".", show_default=True)
def cmd_fav_remove(label, vault):
    """Remove a label from favorites."""
    removed = remove_favorite(vault, label)
    if removed:
        click.echo(f"Removed '{label}' from favorites.")
    else:
        click.echo(f"'{label}' was not in favorites.")


@cmd_favorites.command("list")
@click.option("--vault", default=".", show_default=True)
def cmd_fav_list(vault):
    """List all favorite labels."""
    favs = list_favorites(vault)
    if not favs:
        click.echo("No favorites set.")
    else:
        for f in favs:
            click.echo(f)


@cmd_favorites.command("check")
@click.argument("label")
@click.option("--vault", default=".", show_default=True)
def cmd_fav_check(label, vault):
    """Check if a label is a favorite."""
    if is_favorite(vault, label):
        click.echo(f"'{label}' is a favorite.")
    else:
        click.echo(f"'{label}' is not a favorite.")

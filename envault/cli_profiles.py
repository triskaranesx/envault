"""CLI commands for profile management."""

import click
from envault.profiles import save_profile, get_profile, delete_profile, list_profiles


@click.group("profile")
def cmd_profile():
    """Manage label profiles (named sets of labels)."""
    pass


@cmd_profile.command("save")
@click.argument("name")
@click.argument("labels", nargs=-1, required=True)
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
def cmd_profile_save(name, labels, vault_dir):
    """Save a named profile with the given LABELS."""
    try:
        save_profile(vault_dir, name, list(labels))
        click.echo(f"Profile '{name}' saved with {len(labels)} label(s).")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cmd_profile.command("show")
@click.argument("name")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
def cmd_profile_show(name, vault_dir):
    """Show labels in a named profile."""
    labels = get_profile(vault_dir, name)
    if labels is None:
        click.echo(f"Profile '{name}' not found.", err=True)
        raise SystemExit(1)
    click.echo(f"Profile '{name}':")
    for label in labels:
        click.echo(f"  - {label}")


@cmd_profile.command("delete")
@click.argument("name")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
def cmd_profile_delete(name, vault_dir):
    """Delete a named profile."""
    removed = delete_profile(vault_dir, name)
    if removed:
        click.echo(f"Profile '{name}' deleted.")
    else:
        click.echo(f"Profile '{name}' not found.", err=True)
        raise SystemExit(1)


@cmd_profile.command("list")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
def cmd_profile_list(vault_dir):
    """List all saved profiles."""
    names = list_profiles(vault_dir)
    if not names:
        click.echo("No profiles saved.")
    else:
        for name in names:
            click.echo(name)

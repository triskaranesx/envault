"""CLI commands for managing vault permissions."""

import click
from envault.permissions import (
    set_permission,
    get_permission,
    remove_permission,
    list_permissions,
    VALID_ROLES,
)


@click.group("permissions")
def cmd_permissions():
    """Manage actor permissions for the vault."""


@cmd_permissions.command("set")
@click.argument("actor")
@click.argument("role", type=click.Choice(sorted(VALID_ROLES)))
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
@click.option("--label", default=None, help="Scope permission to a specific label.")
def cmd_perm_set(actor, role, vault_dir, label):
    """Assign ROLE to ACTOR (optionally scoped to a label)."""
    try:
        set_permission(vault_dir, actor, role, label=label)
        scope = f" on label '{label}'" if label else " on vault"
        click.echo(f"Set '{role}' for '{actor}'{scope}.")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cmd_permissions.command("get")
@click.argument("actor")
@click.option("--vault-dir", default=".", show_default=True)
@click.option("--label", default=None)
def cmd_perm_get(actor, vault_dir, label):
    """Show the role assigned to ACTOR."""
    role = get_permission(vault_dir, actor, label=label)
    if role:
        scope = f" (label: {label})" if label else " (vault)"
        click.echo(f"{actor}: {role}{scope}")
    else:
        click.echo(f"No permission found for '{actor}'.")


@cmd_permissions.command("remove")
@click.argument("actor")
@click.option("--vault-dir", default=".", show_default=True)
@click.option("--label", default=None)
def cmd_perm_remove(actor, vault_dir, label):
    """Remove the permission entry for ACTOR."""
    removed = remove_permission(vault_dir, actor, label=label)
    if removed:
        click.echo(f"Removed permission for '{actor}'.")
    else:
        click.echo(f"No permission found for '{actor}'.")


@cmd_permissions.command("list")
@click.option("--vault-dir", default=".", show_default=True)
@click.option("--label", default=None, help="Filter by label scope.")
def cmd_perm_list(vault_dir, label):
    """List all permissions (optionally for a specific label)."""
    entries = list_permissions(vault_dir, label=label)
    if not entries:
        click.echo("No permissions defined.")
        return
    scope = f"label '{label}'" if label else "vault"
    click.echo(f"Permissions for {scope}:")
    for e in entries:
        click.echo(f"  {e['actor']}: {e['role']}")

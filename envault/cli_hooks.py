"""CLI commands for managing vault operation hooks."""

import click

from envault.hooks import VALID_EVENTS, get_hook, list_hooks, remove_hook, set_hook


@click.group("hooks")
def cmd_hooks() -> None:
    """Manage pre/post hooks for vault operations."""


@cmd_hooks.command("set")
@click.argument("event")
@click.argument("command")
@click.option("--vault-dir", default=".", show_default=True, help="Path to vault directory.")
def cmd_hook_set(event: str, command: str, vault_dir: str) -> None:
    """Register COMMAND to run on EVENT.

    Valid events: pre-add, post-add, pre-get, post-get, pre-rotate, post-rotate.
    """
    try:
        set_hook(vault_dir, event, command)
        click.echo(f"Hook set: [{event}] -> {command}")
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


@cmd_hooks.command("get")
@click.argument("event")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_hook_get(event: str, vault_dir: str) -> None:
    """Show the command registered for EVENT."""
    command = get_hook(vault_dir, event)
    if command is None:
        click.echo(f"No hook registered for '{event}'.")
    else:
        click.echo(f"[{event}] {command}")


@cmd_hooks.command("remove")
@click.argument("event")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_hook_remove(event: str, vault_dir: str) -> None:
    """Remove the hook for EVENT."""
    removed = remove_hook(vault_dir, event)
    if removed:
        click.echo(f"Hook for '{event}' removed.")
    else:
        click.echo(f"No hook was registered for '{event}'.")


@cmd_hooks.command("list")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_hook_list(vault_dir: str) -> None:
    """List all registered hooks."""
    hooks = list_hooks(vault_dir)
    if not hooks:
        click.echo("No hooks registered.")
        return
    for event in sorted(VALID_EVENTS):
        if event in hooks:
            click.echo(f"  {event:<16} {hooks[event]}")

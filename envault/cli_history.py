"""CLI commands for viewing vault entry history."""

import click
from envault.history import get_history, clear_history


@click.command("log")
@click.option("--label", default=None, help="Filter history by entry label.")
@click.option("--vault-dir", default=".", hidden=True)
def cmd_log(label: str | None, vault_dir: str) -> None:
    """Show change history for vault entries."""
    entries = get_history(label=label, vault_dir=vault_dir)
    if not entries:
        click.echo("No history found.")
        return
    for entry in entries:
        label_str = click.style(entry["label"], fg="cyan")
        action_str = click.style(entry["action"], fg="yellow")
        click.echo(
            f"[{entry['timestamp']}] {label_str} v{entry['version']} "
            f"— {action_str} by {entry['actor']}"
        )


@click.command("clear-log")
@click.option("--vault-dir", default=".", hidden=True)
@click.confirmation_option(prompt="Clear all history? This cannot be undone.")
def cmd_clear_log(vault_dir: str) -> None:
    """Permanently delete all change history."""
    clear_history(vault_dir=vault_dir)
    click.echo(click.style("History cleared.", fg="red"))

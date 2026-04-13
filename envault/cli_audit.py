"""CLI commands for the envault audit log."""

import click
from envault.audit import get_audit_log, clear_audit_log

DEFAULT_VAULT = ".envault"


@click.command("audit")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True, help="Vault file path.")
@click.option("--label", default=None, help="Filter entries by label.")
@click.option("--action", default=None, help="Filter entries by action type.")
def cmd_audit(vault: str, label: str, action: str) -> None:
    """Show the audit log for vault access and mutations."""
    entries = get_audit_log(vault, label=label, action=action)
    if not entries:
        click.echo("No audit entries found.")
        return
    for e in entries:
        actor_str = f" [{e['actor']}]" if e.get("actor") else ""
        note_str = f" — {e['note']}" if e.get("note") else ""
        click.echo(
            f"{e['timestamp']}  {e['action'].upper():8s}  {e['label']}{actor_str}{note_str}"
        )


@click.command("clear-audit")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True, help="Vault file path.")
@click.confirmation_option(prompt="This will permanently delete all audit records. Continue?")
def cmd_clear_audit(vault: str) -> None:
    """Permanently clear the audit log."""
    clear_audit_log(vault)
    click.echo("Audit log cleared.")

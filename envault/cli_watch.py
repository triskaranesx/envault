"""CLI commands for vault watching / change detection."""

from __future__ import annotations

from pathlib import Path

import click

from .env_watch import has_changed, update_fingerprint, watch_once


@click.group("watch")
def cmd_watch() -> None:
    """Watch vault for changes."""


@cmd_watch.command("status")
@click.argument("vault_dir", default=".", type=click.Path())
def cmd_watch_status(vault_dir: str) -> None:
    """Check whether the vault has changed since last snapshot."""
    vd = Path(vault_dir)
    vault_file = vd / "vault.json"
    if not vault_file.exists():
        click.echo("No vault found.", err=True)
        raise SystemExit(1)
    if has_changed(vd):
        click.echo("CHANGED: vault has been modified since last check.")
    else:
        click.echo("OK: vault is unchanged.")


@cmd_watch.command("mark")
@click.argument("vault_dir", default=".", type=click.Path())
def cmd_watch_mark(vault_dir: str) -> None:
    """Record the current vault fingerprint as the baseline."""
    vd = Path(vault_dir)
    vault_file = vd / "vault.json"
    if not vault_file.exists():
        click.echo("No vault found.", err=True)
        raise SystemExit(1)
    fp = update_fingerprint(vd)
    click.echo(f"Fingerprint recorded: {fp}")


@cmd_watch.command("once")
@click.argument("vault_dir", default=".", type=click.Path())
def cmd_watch_once(vault_dir: str) -> None:
    """Check for a change, print result, and update the baseline."""
    vd = Path(vault_dir)
    vault_file = vd / "vault.json"
    if not vault_file.exists():
        click.echo("No vault found.", err=True)
        raise SystemExit(1)

    def _notify(path: Path) -> None:
        click.echo(f"Change detected in vault at {path}")

    changed = watch_once(vd, _notify)
    if not changed:
        click.echo("No changes detected.")

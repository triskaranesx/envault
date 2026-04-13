"""CLI commands for key rotation."""

from __future__ import annotations

from pathlib import Path

import click

from envault.rotation import rotate_password, rotate_entry


@click.command("rotate")
@click.option("--vault", default=".envault", show_default=True, help="Vault directory.")
@click.option("--label", default=None, help="Rotate a single entry by label (omit for all).")
@click.password_option("--old-password", prompt="Old password", confirmation_prompt=False)
@click.password_option("--new-password", prompt="New password")
def cmd_rotate(vault: str, label: str | None, old_password: str, new_password: str) -> None:
    """Re-encrypt vault entries with a new password."""
    vault_path = Path(vault)

    if not vault_path.exists():
        raise click.ClickException(f"Vault not found: {vault}")

    if old_password == new_password:
        raise click.ClickException("New password must differ from the old password.")

    try:
        if label:
            rotated = rotate_entry(vault_path, label, old_password, new_password)
            if rotated:
                click.echo(f"Rotated entry '{label}'.")
            else:
                raise click.ClickException(f"Entry '{label}' not found.")
        else:
            count = rotate_password(vault_path, old_password, new_password)
            click.echo(f"Rotated {count} entries.")
    except ValueError as exc:
        raise click.ClickException(f"Rotation failed: {exc}") from exc

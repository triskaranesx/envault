"""CLI commands for renaming vault labels."""

from __future__ import annotations

import click

from envault.env_rename import RenameError, rename_label


@click.group("rename")
def cmd_rename() -> None:
    """Rename a label inside the vault."""


@cmd_rename.command("run")
@click.argument("old_label")
@click.argument("new_label")
@click.option(
    "--vault",
    "vault_dir",
    default=".",
    show_default=True,
    help="Path to the vault directory.",
)
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Replace new_label if it already exists.",
)
def cmd_rename_run(
    old_label: str,
    new_label: str,
    vault_dir: str,
    overwrite: bool,
) -> None:
    """Rename OLD_LABEL to NEW_LABEL in the vault.

    All associated metadata (tags, notes, aliases, expiry) is updated
    automatically.
    """
    try:
        rename_label(vault_dir, old_label, new_label, overwrite=overwrite)
    except RenameError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Renamed '{old_label}' → '{new_label}'.")

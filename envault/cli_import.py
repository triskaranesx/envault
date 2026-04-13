"""CLI commands for importing .env files into the vault."""

from __future__ import annotations

from pathlib import Path

import click

from envault.import_env import import_env_file


@click.command("import-env")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--vault",
    default=".envault/vault.json",
    show_default=True,
    help="Path to the vault file.",
    type=click.Path(path_type=Path),
)
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option(
    "--prefix",
    default=None,
    help="Optional prefix to prepend to every imported key (e.g. 'prod').",
)
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite existing entries with the same label.",
)
def cmd_import_env(
    env_file: Path,
    vault: Path,
    password: str,
    prefix: str | None,
    overwrite: bool,
) -> None:
    """Import variables from a .env file into the vault."""
    try:
        result = import_env_file(
            vault_path=vault,
            env_path=env_file,
            password=password,
            prefix=prefix,
            overwrite=overwrite,
        )
        click.echo(
            f"Imported {result['imported']} variable(s), "
            f"skipped {result['skipped']} (already exist)."
        )
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1) from exc

"""CLI commands for managing entry sensitivity levels."""

from __future__ import annotations

import click

from envault.env_sensitivity import (
    SensitivityError,
    filter_by_level,
    get_sensitivity,
    list_sensitivity,
    remove_sensitivity,
    set_sensitivity,
    VALID_LEVELS,
)


@click.group("sensitivity")
def cmd_sensitivity() -> None:
    """Manage sensitivity levels for vault entries."""


@cmd_sensitivity.command("set")
@click.argument("label")
@click.argument("level", type=click.Choice(VALID_LEVELS, case_sensitive=False))
@click.option("--vault-dir", default=".", show_default=True)
def cmd_sensitivity_set(label: str, level: str, vault_dir: str) -> None:
    """Set the sensitivity LEVEL for LABEL."""
    try:
        stored = set_sensitivity(vault_dir, label, level)
        click.echo(f"Sensitivity for '{label}' set to '{stored}'.")
    except SensitivityError as exc:
        raise click.ClickException(str(exc))


@cmd_sensitivity.command("get")
@click.argument("label")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_sensitivity_get(label: str, vault_dir: str) -> None:
    """Get the sensitivity level for LABEL."""
    level = get_sensitivity(vault_dir, label)
    if level is None:
        click.echo(f"No sensitivity set for '{label}'.")
    else:
        click.echo(f"{label}: {level}")


@cmd_sensitivity.command("remove")
@click.argument("label")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_sensitivity_remove(label: str, vault_dir: str) -> None:
    """Remove the sensitivity record for LABEL."""
    removed = remove_sensitivity(vault_dir, label)
    if removed:
        click.echo(f"Sensitivity record for '{label}' removed.")
    else:
        click.echo(f"No sensitivity record found for '{label}'.")


@cmd_sensitivity.command("list")
@click.option("--vault-dir", default=".", show_default=True)
@click.option("--level", type=click.Choice(VALID_LEVELS, case_sensitive=False), default=None)
def cmd_sensitivity_list(vault_dir: str, level: str | None) -> None:
    """List all sensitivity records, optionally filtered by LEVEL."""
    if level:
        labels = filter_by_level(vault_dir, level)
        if not labels:
            click.echo(f"No entries with sensitivity '{level}'.")
        else:
            for lbl in labels:
                click.echo(f"{lbl}: {level}")
    else:
        records = list_sensitivity(vault_dir)
        if not records:
            click.echo("No sensitivity records found.")
        else:
            for rec in records:
                click.echo(f"{rec['label']}: {rec['level']}")

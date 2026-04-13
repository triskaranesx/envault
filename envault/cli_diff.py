"""CLI commands for diffing vault entry versions."""

from __future__ import annotations

import click

from envault.diff import diff_versions, diff_labels


@click.group("diff")
def cmd_diff() -> None:
    """Commands for comparing entry versions."""


@cmd_diff.command("show")
@click.argument("label")
@click.option("--vault", default=".envault", show_default=True, help="Vault directory.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--v1", "version_a", required=True, type=int, help="First version number.")
@click.option("--v2", "version_b", required=True, type=int, help="Second version number.")
def cmd_diff_show(
    label: str,
    vault: str,
    password: str,
    version_a: int,
    version_b: int,
) -> None:
    """Show diff between two versions of a secret LABEL."""
    try:
        result = diff_versions(vault, label, password, version_a, version_b)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Label   : {result['label']}")
    click.echo(f"Version {result['version_a']}: {result['value_a'] if result['value_a'] is not None else '<not found>'}")
    click.echo(f"Version {result['version_b']}: {result['value_b'] if result['value_b'] is not None else '<not found>'}")
    if result["changed"]:
        click.echo("Status  : CHANGED")
    else:
        click.echo("Status  : UNCHANGED")


@cmd_diff.command("versions")
@click.argument("label")
@click.option("--vault", default=".envault", show_default=True, help="Vault directory.")
def cmd_diff_versions(label: str, vault: str) -> None:
    """List available versions for a secret LABEL."""
    try:
        mapping = diff_labels(vault)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc

    versions = mapping.get(label)
    if not versions:
        click.echo(f"No entries found for label '{label}'.")
        return
    click.echo(f"{label}: versions {', '.join(str(v) for v in versions)}")

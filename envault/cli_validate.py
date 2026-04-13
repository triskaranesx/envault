"""CLI commands for validating vault entries."""

from __future__ import annotations

import click

from envault.vault import _load_vault_raw, get_entry
from envault.env_validate import validate_entries


@click.group("validate")
def cmd_validate():
    """Validate vault entries against quality rules."""


@cmd_validate.command("run")
@click.option("--vault", "vault_path", required=True, help="Path to vault directory.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--label", "labels", multiple=True, help="Limit to specific labels.")
@click.option("--strict", is_flag=True, default=False, help="Exit non-zero on warnings too.")
def cmd_validate_run(vault_path: str, password: str, labels: tuple, strict: bool):
    """Run validation rules on all (or selected) vault entries."""
    try:
        raw = _load_vault_raw(vault_path)
    except FileNotFoundError:
        click.echo("Vault not found.", err=True)
        raise SystemExit(1)

    all_labels = list(raw.get("entries", {}).keys())
    target_labels = list(labels) if labels else all_labels

    decrypted: list[dict] = []
    for lbl in target_labels:
        try:
            value = get_entry(vault_path, password, lbl)
            decrypted.append({"label": lbl, "value": value})
        except KeyError:
            click.echo(f"Warning: label '{lbl}' not found — skipped.", err=True)
        except Exception:
            click.echo(f"Warning: could not decrypt '{lbl}' — skipped.", err=True)

    result = validate_entries(decrypted)

    if not result.issues:
        click.echo("✓ All entries passed validation.")
        return

    for issue in result.errors:
        click.echo(f"[ERROR] [{issue.rule}] {issue.message}")
    for issue in result.warnings:
        click.echo(f"[WARN]  [{issue.rule}] {issue.message}")

    click.echo(f"\n{len(result.errors)} error(s), {len(result.warnings)} warning(s).")

    if result.errors or (strict and result.warnings):
        raise SystemExit(1)

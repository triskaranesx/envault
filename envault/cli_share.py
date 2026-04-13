"""CLI commands for sharing vault snapshots with teammates."""

import click

from envault.vault import _load_vault_raw, _save_vault_raw
from envault.sharing import export_snapshot, import_snapshot, merge_entries


@click.command("export")
@click.option("--vault", "vault_path", default=".envault", show_default=True,
              help="Path to the vault file.")
@click.option("--label", default="", help="Optional human-readable snapshot label.")
@click.password_option("--password", prompt="Vault password",
                       confirmation_prompt=False, help="Password to encrypt snapshot.")
def cmd_export(vault_path: str, label: str, password: str) -> None:
    """Export an encrypted snapshot token for sharing."""
    try:
        vault = _load_vault_raw(vault_path)
    except FileNotFoundError:
        raise click.ClickException(f"Vault not found: {vault_path}. Run 'envault init' first.")

    token = export_snapshot(vault, password, label=label or None)
    click.echo("Share this token with your teammate:\n")
    click.echo(token)


@click.command("import")
@click.argument("token")
@click.option("--vault", "vault_path", default=".envault", show_default=True,
              help="Path to the vault file.")
@click.option("--merge", "do_merge", is_flag=True, default=False,
              help="Merge incoming entries instead of replacing.")
@click.password_option("--password", prompt="Snapshot password",
                       confirmation_prompt=False, help="Password used to encrypt the token.")
def cmd_import(token: str, vault_path: str, do_merge: bool, password: str) -> None:
    """Import a shared snapshot token into the local vault."""
    try:
        payload = import_snapshot(token, password)
    except ValueError as exc:
        raise click.ClickException(str(exc))

    incoming = payload.get("entries", [])

    if do_merge:
        try:
            vault = _load_vault_raw(vault_path)
        except FileNotFoundError:
            vault = {"entries": [], "index": 0}
        vault["entries"] = merge_entries(vault.get("entries", []), incoming)
        action = "Merged"
    else:
        try:
            vault = _load_vault_raw(vault_path)
        except FileNotFoundError:
            vault = {"entries": [], "index": 0}
        vault["entries"] = incoming
        action = "Imported"

    vault["index"] = len(vault["entries"])
    _save_vault_raw(vault_path, vault)

    snap_label = payload.get("label") or "(unlabelled)"
    click.echo(
        f"{action} {len(incoming)} entr(ies) from snapshot '{snap_label}' "
        f"(exported at {payload.get('exported_at', 'unknown')})."
    )

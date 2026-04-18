"""CLI commands for TTL management."""
import click
from envault.env_ttl import set_ttl, get_ttl, remove_ttl, is_expired, list_expired, list_ttls


@click.group("ttl")
def cmd_ttl():
    """Manage time-to-live for vault entries."""


@cmd_ttl.command("set")
@click.argument("label")
@click.argument("seconds", type=int)
@click.option("--vault", "vault_dir", default=".", show_default=True)
def cmd_ttl_set(label, seconds, vault_dir):
    """Set TTL of SECONDS for LABEL."""
    try:
        iso = set_ttl(vault_dir, label, seconds)
        click.echo(f"TTL set for '{label}': expires at {iso}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cmd_ttl.command("get")
@click.argument("label")
@click.option("--vault", "vault_dir", default=".", show_default=True)
def cmd_ttl_get(label, vault_dir):
    """Show TTL info for LABEL."""
    record = get_ttl(vault_dir, label)
    if record is None:
        click.echo(f"No TTL set for '{label}'.")
    else:
        expired = is_expired(vault_dir, label)
        status = "EXPIRED" if expired else "active"
        click.echo(f"Label: {label}")
        click.echo(f"Expires at: {record['expires_at']}")
        click.echo(f"Status: {status}")


@cmd_ttl.command("remove")
@click.argument("label")
@click.option("--vault", "vault_dir", default=".", show_default=True)
def cmd_ttl_remove(label, vault_dir):
    """Remove TTL for LABEL."""
    removed = remove_ttl(vault_dir, label)
    if removed:
        click.echo(f"TTL removed for '{label}'.")
    else:
        click.echo(f"No TTL found for '{label}'.")


@cmd_ttl.command("list")
@click.option("--vault", "vault_dir", default=".", show_default=True)
@click.option("--expired-only", is_flag=True, default=False)
def cmd_ttl_list(vault_dir, expired_only):
    """List all TTL entries."""
    if expired_only:
        labels = list_expired(vault_dir)
        if not labels:
            click.echo("No expired entries.")
        for label in labels:
            click.echo(f"{label} [EXPIRED]")
    else:
        data = list_ttls(vault_dir)
        if not data:
            click.echo("No TTL entries set.")
        for label, record in data.items():
            expired = is_expired(vault_dir, label)
            status = "EXPIRED" if expired else "active"
            click.echo(f"{label}: expires={record['expires_at']} [{status}]")

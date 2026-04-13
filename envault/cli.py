"""CLI entry points for envault using Click."""

import sys
from pathlib import Path

import click

from envault.vault import (
    add_entry,
    get_entry,
    init_vault,
    list_entries,
    load_vault,
    save_vault,
    DEFAULT_VAULT_FILE,
)

VAULT_OPTION = click.option(
    "--vault",
    default=DEFAULT_VAULT_FILE,
    show_default=True,
    help="Path to the vault file.",
)


@click.group()
def cli():
    """envault — encrypt and version your .env files."""


@cli.command("init")
@VAULT_OPTION
def cmd_init(vault):
    """Initialise a new empty vault."""
    vault_path = Path(vault)
    if vault_path.exists():
        click.echo(f"Vault already exists at {vault_path}", err=True)
        sys.exit(1)
    v = init_vault(vault_path)
    save_vault(v, vault_path)
    click.echo(f"Initialised new vault at {vault_path}")


@cli.command("add")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--label", default="", help="Optional label for this version.")
@VAULT_OPTION
def cmd_add(env_file, label, vault):
    """Encrypt ENV_FILE and add it as a new vault entry."""
    vault_path = Path(vault)
    password = click.prompt("Password", hide_input=True)
    try:
        v = load_vault(vault_path)
    except FileNotFoundError:
        click.echo(f"Vault not found at {vault_path}. Run `envault init` first.", err=True)
        sys.exit(1)
    content = Path(env_file).read_text()
    entry = add_entry(v, password, content, label=label or None)
    save_vault(v, vault_path)
    click.echo(f"Added entry #{entry['index']} to vault.")


@cli.command("get")
@click.option("--index", default=-1, show_default=True, help="Entry index (default: latest).")
@click.option("--output", "-o", default=None, help="Write decrypted content to this file.")
@VAULT_OPTION
def cmd_get(index, output, vault):
    """Decrypt and print (or save) a vault entry."""
    vault_path = Path(vault)
    password = click.prompt("Password", hide_input=True)
    try:
        v = load_vault(vault_path)
        content = get_entry(v, password, index=index)
    except FileNotFoundError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Failed to decrypt: {exc}", err=True)
        sys.exit(1)
    if output:
        Path(output).write_text(content)
        click.echo(f"Decrypted content written to {output}")
    else:
        click.echo(content, nl=False)


@cli.command("list")
@VAULT_OPTION
def cmd_list(vault):
    """List all entries in the vault."""
    vault_path = Path(vault)
    try:
        v = load_vault(vault_path)
    except FileNotFoundError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)
    entries = list_entries(v)
    if not entries:
        click.echo("No entries found.")
        return
    for e in entries:
        import datetime
        ts = datetime.datetime.fromtimestamp(e["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
        label = f"  [{e['label']}]" if e["label"] else ""
        click.echo(f"  #{e['index']}  {ts}{label}")


if __name__ == "__main__":
    cli()

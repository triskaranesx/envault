"""CLI commands for exporting .env files from the vault."""

import click
from pathlib import Path

from .export_env import export_env
from .audit import record_access


@click.group("export")
def cmd_export_env():
    """Export vault entries as .env file format."""
    pass


@cmd_export_env.command("env")
@click.argument("vault_dir", type=click.Path(exists=True))
@click.option("--password", "-p", prompt=True, hide_input=True, help="Vault password.")
@click.option(
    "--output", "-o", default=None, type=click.Path(),
    help="Output file path. Defaults to stdout."
)
@click.option(
    "--label", "-l", multiple=True,
    help="Filter by label (can be repeated). Exports all if omitted."
)
@click.option(
    "--actor", default="cli",
    help="Actor name recorded in audit log (default: cli)."
)
def cmd_env(
    vault_dir: str,
    password: str,
    output: str | None,
    label: tuple[str, ...],
    actor: str,
) -> None:
    """Export vault secrets as a .env-formatted file.

    VAULT_DIR is the path to the initialised envault directory.

    Examples:

    \b
        # Print all entries to stdout
        envault export env ./my-vault

    \b
        # Write selected labels to a file
        envault export env ./my-vault -l DB_URL -l API_KEY -o .env
    """
    vault_path = Path(vault_dir)
    labels: list[str] | None = list(label) if label else None

    try:
        env_text = export_env(vault_path, password, labels=labels)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    except FileNotFoundError:
        raise click.ClickException(
            f"Vault not found at '{vault_dir}'. Run 'envault init' first."
        )

    # Record each exported label in the audit log
    exported_labels = labels if labels else _parse_labels_from_env(env_text)
    for lbl in exported_labels:
        record_access(vault_path, lbl, actor=actor, action="export-env")

    if output:
        out_path = Path(output)
        out_path.write_text(env_text, encoding="utf-8")
        click.echo(f"Exported {len(exported_labels)} label(s) to '{out_path}'.")
    else:
        click.echo(env_text, nl=False)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_labels_from_env(env_text: str) -> list[str]:
    """Extract variable names from an exported .env string.

    Lines that start with '#' or are blank are skipped.
    """
    labels: list[str] = []
    for line in env_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            labels.append(line.split("=", 1)[0])
    return labels

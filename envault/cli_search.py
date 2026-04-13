"""CLI commands for searching vault entries."""

import click

from envault.search import search_entries


@click.command("search")
@click.option("--label", "-l", default=None, help="Wildcard pattern for label (e.g. DB_*).")
@click.option("--tag", "-t", default=None, help="Filter by exact tag name.")
@click.option("--value", "-v", default=None, help="Wildcard pattern for decrypted value.")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
@click.password_option("--password", "-p", prompt="Master password", confirmation_prompt=False)
def cmd_search(label, tag, value, vault_dir, password):
    """Search vault entries by label pattern, tag, or value pattern."""
    if label is None and tag is None and value is None:
        raise click.UsageError(
            "Provide at least one filter: --label, --tag, or --value."
        )

    try:
        results = search_entries(
            vault_dir=vault_dir,
            password=password,
            label_pattern=label,
            tag=tag,
            value_pattern=value,
        )
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc

    if not results:
        click.echo("No entries matched your search.")
        return

    click.echo(f"Found {len(results)} entry/entries:\n")
    for entry in results:
        tags_str = ", ".join(entry["tags"]) if entry["tags"] else "(none)"
        click.echo(
            f"  [{entry['index']}] {entry['label']}\n"
            f"       value : {entry['value']}\n"
            f"       tags  : {tags_str}"
        )

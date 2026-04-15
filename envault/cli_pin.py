"""CLI commands for managing entry pins in envault."""

import click
from envault.env_pin import pin_entry, unpin_entry, get_pin, list_pins


@click.group(name="pin")
def cmd_pin():
    """Manage pinned (required) values for vault entries."""


@cmd_pin.command(name="set")
@click.argument("label")
@click.argument("value")
@click.option("--vault", default=".", show_default=True, help="Path to vault directory.")
def cmd_pin_set(label, value, vault):
    """Pin LABEL to a required VALUE."""
    try:
        pin_entry(vault, label, value)
        click.echo(f"Pinned '{label}' to '{value}'.")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_pin.command(name="remove")
@click.argument("label")
@click.option("--vault", default=".", show_default=True, help="Path to vault directory.")
def cmd_pin_remove(label, vault):
    """Remove the pin for LABEL."""
    removed = unpin_entry(vault, label)
    if removed:
        click.echo(f"Pin removed for '{label}'.")
    else:
        click.echo(f"No pin found for '{label}'.")


@cmd_pin.command(name="get")
@click.argument("label")
@click.option("--vault", default=".", show_default=True, help="Path to vault directory.")
def cmd_pin_get(label, vault):
    """Show the pinned value for LABEL."""
    value = get_pin(vault, label)
    if value is None:
        click.echo(f"No pin set for '{label}'.")
    else:
        click.echo(f"{label}={value}")


@cmd_pin.command(name="list")
@click.option("--vault", default=".", show_default=True, help="Path to vault directory.")
def cmd_pin_list(vault):
    """List all pinned entries."""
    pins = list_pins(vault)
    if not pins:
        click.echo("No pins defined.")
        return
    for label, value in pins.items():
        click.echo(f"  {label} = {value}")


@cmd_pin.command(name="check")
@click.option("--vault", default=".", show_default=True, help="Path to vault directory.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
def cmd_pin_check(vault, password):
    """Check current vault values against all pins."""
    from envault.vault import list_entries, get_entry
    from envault.env_pin import check_pins

    entries = list_entries(vault)
    resolved = {}
    for entry in entries:
        label = entry["label"]
        try:
            resolved[label] = get_entry(vault, label, password)
        except Exception:
            resolved[label] = None

    violations = check_pins(vault, resolved)
    if not violations:
        click.echo("All pins satisfied.")
    else:
        for v in violations:
            actual_display = repr(v["actual"]) if v["actual"] is not None else "<missing>"
            click.echo(f"  FAIL '{v['label']}': expected {repr(v['expected'])}, got {actual_display}")
        raise SystemExit(1)

"""CLI commands for managing envault templates."""

import click
from envault.templates import save_template, get_template, delete_template, list_templates


@click.group("template")
def cmd_template():
    """Manage entry templates (named sets of labels)."""
    pass


@cmd_template.command("save")
@click.argument("name")
@click.argument("labels", nargs=-1, required=True)
@click.option("--vault", default=".", show_default=True, help="Path to vault directory.")
def cmd_template_save(name, labels, vault):
    """Save a named template with the given LABELS."""
    try:
        save_template(vault, name, list(labels))
        click.echo(f"Template '{name}' saved with {len(labels)} label(s).")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cmd_template.command("show")
@click.argument("name")
@click.option("--vault", default=".", show_default=True, help="Path to vault directory.")
def cmd_template_show(name, vault):
    """Show the labels in a named template."""
    labels = get_template(vault, name)
    if labels is None:
        click.echo(f"Template '{name}' not found.", err=True)
        raise SystemExit(1)
    click.echo(f"Template '{name}':")
    for label in labels:
        click.echo(f"  - {label}")


@cmd_template.command("delete")
@click.argument("name")
@click.option("--vault", default=".", show_default=True, help="Path to vault directory.")
def cmd_template_delete(name, vault):
    """Delete a named template."""
    deleted = delete_template(vault, name)
    if deleted:
        click.echo(f"Template '{name}' deleted.")
    else:
        click.echo(f"Template '{name}' not found.", err=True)
        raise SystemExit(1)


@cmd_template.command("list")
@click.option("--vault", default=".", show_default=True, help="Path to vault directory.")
def cmd_template_list(vault):
    """List all saved templates."""
    templates = list_templates(vault)
    if not templates:
        click.echo("No templates saved.")
        return
    for name, labels in templates.items():
        click.echo(f"{name}: {', '.join(labels)}")

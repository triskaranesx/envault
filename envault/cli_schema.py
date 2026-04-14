"""CLI commands for managing env schema definitions.

Allows users to define expected fields, types, and requirements
for a vault's environment variables.
"""

import click
from pathlib import Path

from .env_schema import load_schema, save_schema, set_field, remove_field, validate_against_schema


@click.group("schema")
def cmd_schema():
    """Manage the env variable schema for a vault."""
    pass


@cmd_schema.command("set")
@click.argument("vault_path")
@click.argument("label")
@click.option("--type", "field_type", default="string",
              type=click.Choice(["string", "integer", "boolean", "url", "email"]),
              show_default=True, help="Expected type for the field.")
@click.option("--required/--optional", default=False, show_default=True,
              help="Whether the field is required.")
@click.option("--description", default="", help="Human-readable description of the field.")
@click.option("--pattern", default=None, help="Optional regex pattern the value must match.")
def cmd_schema_set(vault_path, label, field_type, required, description, pattern):
    """Define or update a schema field for LABEL."""
    vault_dir = Path(vault_path)
    try:
        set_field(
            vault_dir,
            label=label,
            field_type=field_type,
            required=required,
            description=description,
            pattern=pattern,
        )
        click.echo(f"Schema field '{label}' set (type={field_type}, required={required}).")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_schema.command("remove")
@click.argument("vault_path")
@click.argument("label")
def cmd_schema_remove(vault_path, label):
    """Remove schema definition for LABEL."""
    vault_dir = Path(vault_path)
    removed = remove_field(vault_dir, label)
    if removed:
        click.echo(f"Schema field '{label}' removed.")
    else:
        click.echo(f"No schema entry found for '{label}'.")


@cmd_schema.command("show")
@click.argument("vault_path")
@click.argument("label")
def cmd_schema_show(vault_path, label):
    """Show schema definition for LABEL."""
    vault_dir = Path(vault_path)
    schema = load_schema(vault_dir)
    field = schema.get(label)
    if field is None:
        click.echo(f"No schema defined for '{label}'.")
        return
    click.echo(f"Label:       {label}")
    click.echo(f"Type:        {field.get('type', 'string')}")
    click.echo(f"Required:    {field.get('required', False)}")
    click.echo(f"Description: {field.get('description', '')}")
    pattern = field.get('pattern')
    if pattern:
        click.echo(f"Pattern:     {pattern}")


@cmd_schema.command("list")
@click.argument("vault_path")
def cmd_schema_list(vault_path):
    """List all schema-defined fields for the vault."""
    vault_dir = Path(vault_path)
    schema = load_schema(vault_dir)
    if not schema:
        click.echo("No schema fields defined.")
        return
    for label, field in sorted(schema.items()):
        req = "required" if field.get("required") else "optional"
        ftype = field.get("type", "string")
        desc = field.get("description", "")
        suffix = f" — {desc}" if desc else ""
        click.echo(f"  {label}  [{ftype}, {req}]{suffix}")


@cmd_schema.command("validate")
@click.argument("vault_path")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def cmd_schema_validate(vault_path, password):
    """Validate vault entries against the defined schema."""
    vault_dir = Path(vault_path)
    try:
        issues = validate_against_schema(vault_dir, password)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    if not issues:
        click.echo("All entries conform to schema.")
        return

    click.echo(f"{len(issues)} issue(s) found:")
    for issue in issues:
        level = issue.get("level", "error").upper()
        label = issue.get("label", "?")
        message = issue.get("message", "")
        click.echo(f"  [{level}] {label}: {message}")
    raise SystemExit(1)

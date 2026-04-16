"""CLI commands for schema-based validation of imported env entries."""
import click
from envault.import_env import parse_env_file
from envault.env_import_schema import validate_against_schema, errors_only


@click.group("schema-validate")
def cmd_schema_validate():
    """Validate .env files against vault schema."""


@cmd_schema_validate.command("run")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--vault-dir", default=".", show_default=True, help="Path to vault directory.")
@click.option("--strict", is_flag=True, default=False, help="Exit non-zero on warnings too.")
def cmd_schema_validate_run(env_file, vault_dir, strict):
    """Validate ENV_FILE entries against the vault schema."""
    pairs = parse_env_file(env_file)
    entries = dict(pairs)
    violations = validate_against_schema(vault_dir, entries)

    if not violations:
        click.echo("All entries are valid.")
        return

    has_error = False
    for v in violations:
        prefix = "ERROR" if v.level == "error" else "WARN "
        click.echo(f"[{prefix}] {v.label}: {v.message}")
        if v.level == "error":
            has_error = True

    if has_error or strict:
        raise SystemExit(1)


@cmd_schema_validate.command("check")
@click.argument("label")
@click.argument("value")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_schema_validate_check(label, value, vault_dir):
    """Check a single LABEL=VALUE pair against the vault schema."""
    violations = validate_against_schema(vault_dir, {label: value})
    relevant = [v for v in violations if v.label == label]
    if not relevant:
        click.echo(f"{label}: OK")
    else:
        for v in relevant:
            click.echo(f"[{v.level.upper()}] {v.label}: {v.message}")
        if errors_only(relevant):
            raise SystemExit(1)

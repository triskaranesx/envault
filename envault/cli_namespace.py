"""CLI commands for namespace management."""

import click
from envault.env_namespace import (
    set_namespace,
    get_namespace,
    remove_namespace,
    list_namespaces,
    get_labels_in_namespace,
    NamespaceError,
)


@click.group("namespace")
def cmd_namespace():
    """Manage label namespaces."""


@cmd_namespace.command("set")
@click.argument("label")
@click.argument("namespace")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def cmd_ns_set(label, namespace, vault):
    """Assign LABEL to NAMESPACE."""
    try:
        set_namespace(vault, label, namespace)
        click.echo(f"Assigned '{label}' to namespace '{namespace}'.")
    except NamespaceError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cmd_namespace.command("get")
@click.argument("label")
@click.option("--vault", default=".", show_default=True)
def cmd_ns_get(label, vault):
    """Show the namespace for LABEL."""
    ns = get_namespace(vault, label)
    if ns is None:
        click.echo(f"No namespace set for '{label}'.")
    else:
        click.echo(ns)


@cmd_namespace.command("remove")
@click.argument("label")
@click.option("--vault", default=".", show_default=True)
def cmd_ns_remove(label, vault):
    """Remove namespace assignment for LABEL."""
    removed = remove_namespace(vault, label)
    if removed:
        click.echo(f"Removed namespace for '{label}'.")
    else:
        click.echo(f"No namespace found for '{label}'.")


@cmd_namespace.command("list")
@click.option("--vault", default=".", show_default=True)
@click.option("--ns", default=None, help="Filter by namespace.")
def cmd_ns_list(vault, ns):
    """List all namespace assignments, optionally filtered by --ns."""
    if ns:
        labels = get_labels_in_namespace(vault, ns)
        if not labels:
            click.echo(f"No labels in namespace '{ns}'.")
        else:
            for label in labels:
                click.echo(label)
    else:
        data = list_namespaces(vault)
        if not data:
            click.echo("No namespaces defined.")
        else:
            for label, namespace in sorted(data.items()):
                click.echo(f"{label}: {namespace}")

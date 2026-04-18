"""CLI commands for managing per-label comments."""
import click
from envault.env_comments import set_comment, get_comment, remove_comment, list_comments


@click.group("comments")
def cmd_comments():
    """Manage inline comments for vault entries."""


@cmd_comments.command("set")
@click.argument("label")
@click.argument("comment")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_comment_set(label, comment, vault_dir):
    """Set a comment for a label."""
    try:
        set_comment(vault_dir, label, comment)
        click.echo(f"Comment set for '{label}'.")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cmd_comments.command("get")
@click.argument("label")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_comment_get(label, vault_dir):
    """Get the comment for a label."""
    c = get_comment(vault_dir, label)
    if c is None:
        click.echo(f"No comment set for '{label}'.")
    else:
        click.echo(c)


@cmd_comments.command("remove")
@click.argument("label")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_comment_remove(label, vault_dir):
    """Remove the comment for a label."""
    removed = remove_comment(vault_dir, label)
    if removed:
        click.echo(f"Comment removed for '{label}'.")
    else:
        click.echo(f"No comment found for '{label}'.")


@cmd_comments.command("list")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_comment_list(vault_dir):
    """List all comments."""
    data = list_comments(vault_dir)
    if not data:
        click.echo("No comments set.")
    else:
        for label, comment in sorted(data.items()):
            click.echo(f"{label}: {comment}")

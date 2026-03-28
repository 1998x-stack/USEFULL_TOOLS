"""devkit CLI entry point."""

import os

import click

from devkit import __version__


@click.group()
@click.version_option(version=__version__, prog_name="devkit")
def cli():
    """devkit - A Swiss Army Knife for Developers.

    27+ ready-to-use CLI tools for file conversion, text processing,
    AI/LLM utilities, data handling, and more.
    """
    pass


@cli.group()
def convert():
    """Document & media conversion tools."""
    pass


@cli.group()
def text():
    """Text & NLP processing tools."""
    pass


@cli.group()
def files():
    """File management tools."""
    pass


@cli.group()
def ai():
    """AI/LLM utility tools."""
    pass


@cli.group()
def data():
    """Data processing tools."""
    pass


@cli.group()
def web():
    """Web utility tools."""
    pass


@cli.group()
def dev():
    """Developer utility tools."""
    pass


# --- Dev commands ---

@dev.command("hash")
@click.argument("input_value")
@click.option("--algo", default="sha256", type=click.Choice(["md5", "sha1", "sha256", "sha512"]))
@click.option("--file", "is_file", is_flag=True, help="Treat input as a file path")
def dev_hash(input_value, algo, is_file):
    """Hash a string or file."""
    from devkit.dev.hash_tool import hash_string, hash_file
    if is_file:
        result = hash_file(input_value, algo=algo)
        if result is None:
            click.echo(f"Error: File not found: {input_value}", err=True)
            raise SystemExit(1)
    else:
        result = hash_string(input_value, algo=algo)
    click.echo(result)


@dev.command("ports")
@click.option("--range", "port_range", default="3000-9000", help="Port range (e.g., 3000-9000)")
@click.option("--count", default=5, help="Number of ports to find")
def dev_ports(port_range, count):
    """Find available network ports."""
    from devkit.dev.port_finder import find_available_ports
    start, end = map(int, port_range.split("-"))
    ports = find_available_ports(start=start, end=end, count=count)
    if ports:
        click.echo(f"Available ports ({len(ports)} found):")
        for port in ports:
            click.echo(f"  {port}")
    else:
        click.echo("No available ports found in range.", err=True)


@dev.command("env-check")
@click.option("--tools", default=None, help="Comma-separated tool names to check")
def dev_env_check(tools):
    """Check development environment for required tools."""
    from devkit.dev.env_checker import check_environment, format_report
    tool_list = tools.split(",") if tools else None
    results = check_environment(tools=tool_list)
    click.echo(format_report(results))


@dev.command("git-stats")
@click.option("--path", default=".", help="Path to git repository")
def dev_git_stats(path):
    """Show git repository statistics."""
    from devkit.dev.git_stats import get_stats
    stats = get_stats(path)
    if "error" in stats:
        click.echo(f"Error: {stats['error']}", err=True)
        raise SystemExit(1)
    click.echo(f"Total commits: {stats['total_commits']}")
    click.echo(f"Total files: {stats['file_count']}")
    click.echo(f"Contributors: {len(stats['contributors'])}")
    if stats["contributors"]:
        click.echo("\nTop contributors:")
        for c in stats["contributors"][:10]:
            click.echo(f"  {c['name']}: {c['commits']} commits")


if __name__ == "__main__":
    cli()

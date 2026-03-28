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


# --- Files commands ---

@files.command("dedup")
@click.argument("directory")
@click.option("--extensions", default="pdf,mp3,mp4,html", help="Comma-separated extensions")
@click.option("--dry-run/--execute", default=True, help="Preview vs actually delete")
def files_dedup(directory, extensions, dry_run):
    """Find and remove duplicate files."""
    from devkit.files.dedup import remove_duplicates
    ext_list = [f"*.{e.strip()}" for e in extensions.split(",")]
    removed = remove_duplicates(directory, ext_list, dry_run=dry_run)
    action = "Would remove" if dry_run else "Removed"
    for f in removed:
        click.echo(f"  {action}: {f}")
    click.echo(f"\n{len(removed)} duplicate(s) {'found' if dry_run else 'removed'}.")


@files.command("search")
@click.argument("file")
@click.argument("query")
@click.option("--context", default=3, help="Lines of context around matches")
def files_search(file, query, context):
    """Search for text in a file."""
    from devkit.files.search_log import search_file
    results = search_file(file, query, context_lines=context)
    if not results:
        click.echo(f"No matches for '{query}' in {file}")
        return
    for r in results:
        click.echo(f"\n--- Line {r['line_number']} ---")
        for line in r["context"]:
            click.echo(f"  {line}")
    click.echo(f"\n{len(results)} match(es) found.")


@files.command("extract-code")
@click.argument("directory")
@click.option("-o", "--output", default=None, help="Output file path")
@click.option("--extensions", default="py,js,ts,html,css", help="Comma-separated extensions")
def files_extract_code(directory, output, extensions):
    """Extract and merge source code files."""
    from devkit.files.extract_code import extract_code_files
    ext_list = [e.strip() for e in extensions.split(",")]
    result = extract_code_files(directory, extensions=ext_list, output=output)
    if output:
        click.echo(f"Code extracted to {output}")
    else:
        click.echo(result)


@files.command("rename")
@click.argument("directory")
@click.option("--pattern", required=True, help="Rename pattern (e.g., 'img_{n:03d}.jpg')")
@click.option("--dry-run/--execute", default=True, help="Preview vs actually rename")
def files_rename(directory, pattern, dry_run):
    """Batch rename files with pattern templates."""
    from devkit.files.batch_rename import batch_rename
    renames = batch_rename(directory, pattern, dry_run=dry_run)
    for old, new in renames:
        click.echo(f"  {os.path.basename(old)} -> {os.path.basename(new)}")
    action = "Would rename" if dry_run else "Renamed"
    click.echo(f"\n{action} {len(renames)} file(s).")


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

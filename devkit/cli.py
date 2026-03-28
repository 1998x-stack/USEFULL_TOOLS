"""devkit CLI entry point."""

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


if __name__ == "__main__":
    cli()

"""Test CLI entry point."""

from click.testing import CliRunner

from devkit.cli import cli


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Swiss Army Knife" in result.output


def test_subgroups_exist():
    runner = CliRunner()
    for group in ["convert", "text", "files", "ai", "data", "web", "dev"]:
        result = runner.invoke(cli, [group, "--help"])
        assert result.exit_code == 0, f"Subgroup '{group}' failed"

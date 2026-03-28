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


# --- Text commands ---

@text.command("length")
@click.argument("text_input")
def text_length(text_input):
    """Calculate information-weighted text length."""
    from devkit.text.text_length import calculate_custom_length
    if os.path.isfile(text_input):
        with open(text_input, "r", encoding="utf-8") as f:
            text_input = f.read()
    result = calculate_custom_length(text_input)
    click.echo(f"Weighted length: {result}")


@text.command("keywords")
@click.argument("text_input")
@click.option("--lang", default="zh", type=click.Choice(["zh", "en"]))
@click.option("--mode", default="all", type=click.Choice(["all", "filter"]))
@click.option("--top", default=10, type=int)
def text_keywords(text_input, lang, mode, top):
    """Extract weighted keywords from text."""
    from devkit.text.keywords import extract_keywords
    if os.path.isfile(text_input):
        with open(text_input, "r", encoding="utf-8") as f:
            text_input = f.read()
    results = extract_keywords(text_input, lang=lang, mode=mode, top_k=top)
    for kw in results:
        click.echo(f"  {kw['word']:<20} boost={kw['boost']:.2f}")


@text.command("split")
@click.argument("text_input")
@click.option("--criterion", default="coarse", type=click.Choice(["coarse", "fine"]))
def text_split(text_input, criterion):
    """Split text into sentences."""
    from devkit.text.split_sentence import split_sentence
    if os.path.isfile(text_input):
        with open(text_input, "r", encoding="utf-8") as f:
            text_input = f.read()
    sentences = split_sentence(text_input, criterion=criterion)
    for i, s in enumerate(sentences, 1):
        click.echo(f"  [{i}] {s}")


@text.command("char-count")
@click.argument("text_input")
def text_char_count(text_input):
    """Count characters by category."""
    from devkit.text.tokenizer import char_count
    if os.path.isfile(text_input):
        with open(text_input, "r", encoding="utf-8") as f:
            text_input = f.read()
    counts = char_count(text_input)
    for category, count in counts.items():
        click.echo(f"  {category:<12} {count}")


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


# --- AI commands ---

@ai.command("tokens")
@click.argument("text_or_file")
@click.option("--model", default="gpt-4o", help="Model name for tokenization")
@click.option("--file", "is_file", is_flag=True, help="Treat input as file path")
def ai_tokens(text_or_file, model, is_file):
    """Count tokens for LLM models."""
    from devkit.ai.token_counter import count_tokens, count_tokens_file
    if is_file:
        count = count_tokens_file(text_or_file, model=model)
    else:
        count = count_tokens(text_or_file, model=model)
    click.echo(f"Tokens ({model}): {count}")


@ai.command("cost")
@click.option("--model", required=True, help="Model name")
@click.option("--input-tokens", required=True, type=int, help="Input token count")
@click.option("--output-tokens", required=True, type=int, help="Output token count")
def ai_cost(model, input_tokens, output_tokens):
    """Estimate API cost."""
    from devkit.ai.cost_calculator import calculate_cost
    cost = calculate_cost(model, input_tokens, output_tokens)
    if cost is None:
        click.echo(f"Unknown model: {model}", err=True)
        raise SystemExit(1)
    click.echo(f"Estimated cost for {model}: ${cost:.6f}")


@ai.command("cost-compare")
@click.option("--input-tokens", required=True, type=int, help="Input token count")
@click.option("--output-tokens", required=True, type=int, help="Output token count")
def ai_cost_compare(input_tokens, output_tokens):
    """Compare API costs across models."""
    from devkit.ai.cost_calculator import compare_costs
    costs = compare_costs(input_tokens, output_tokens)
    click.echo(f"Cost comparison ({input_tokens} in / {output_tokens} out):\n")
    for model, cost in costs.items():
        click.echo(f"  {model:<20} ${cost:.6f}")


@ai.command("prompt")
@click.argument("name")
@click.option("--vars", "variables", default=None, help="JSON variables for rendering")
@click.option("--save", "content", default=None, help="Save content as template")
@click.option("--list", "list_all", is_flag=True, help="List all templates")
def ai_prompt(name, variables, content, list_all):
    """Manage prompt templates."""
    import json as json_mod
    from devkit.ai.prompt_template import render_template, save_template, load_template, list_templates
    if list_all:
        for t in list_templates():
            click.echo(f"  {t}")
        return
    if content:
        path = save_template(name, content)
        click.echo(f"Template saved: {path}")
        return
    template = load_template(name)
    if template is None:
        click.echo(f"Template not found: {name}", err=True)
        raise SystemExit(1)
    if variables:
        vars_dict = json_mod.loads(variables)
        click.echo(render_template(template, vars_dict))
    else:
        click.echo(template)


@cli.group()
def data():
    """Data processing tools."""
    pass


# --- Data commands ---

@data.command("json-flatten")
@click.argument("input_file")
@click.option("-o", "--output", default=None, help="Output file")
def data_json_flatten(input_file, output):
    """Flatten nested JSON to dot-notation keys."""
    import json as json_mod
    from devkit.data.json_utils import flatten_json
    with open(input_file, "r", encoding="utf-8") as f:
        original = json_mod.load(f)
    result = flatten_json(original)
    out = json_mod.dumps(result, indent=2, ensure_ascii=False)
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(out)
        click.echo(f"Flattened JSON written to {output}")
    else:
        click.echo(out)


@data.command("json-merge")
@click.argument("files", nargs=-1, required=True)
@click.option("-o", "--output", required=True, help="Output JSONL file")
def data_json_merge(files, output):
    """Merge multiple JSONL files."""
    from devkit.data.json_utils import merge_jsonl
    merge_jsonl(list(files), output)
    click.echo(f"Merged {len(files)} files into {output}")


@data.command("csv-merge")
@click.argument("files", nargs=-1, required=True)
@click.option("-o", "--output", required=True, help="Output CSV file")
def data_csv_merge(files, output):
    """Merge multiple CSV files."""
    from devkit.data.csv_utils import merge_csvs
    merge_csvs(list(files), output)
    click.echo(f"Merged {len(files)} files into {output}")


@data.command("csv-split")
@click.argument("input_file")
@click.option("--rows", required=True, type=int, help="Rows per file")
@click.option("-o", "--output-dir", default="./splits", help="Output directory")
def data_csv_split(input_file, rows, output_dir):
    """Split a large CSV into smaller files."""
    from devkit.data.csv_utils import split_csv
    result = split_csv(input_file, rows, output_dir)
    click.echo(f"Split into {len(result)} files in {output_dir}")


@data.command("excel2csv")
@click.argument("input_file")
@click.option("-o", "--output", default=None, help="Output CSV file")
@click.option("--sheet", default=None, help="Sheet name")
def data_excel2csv(input_file, output, sheet):
    """Convert Excel to CSV."""
    from devkit.data.excel2csv import excel_to_csv
    if output is None:
        output = input_file.rsplit(".", 1)[0] + ".csv"
    excel_to_csv(input_file, output, sheet=sheet)
    click.echo(f"Converted to {output}")


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

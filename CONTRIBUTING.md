# Contributing to devkit

Contributions are welcome. The repository's public installation/package name
conflict and file-operation constraints are documented in [Safety](docs/SAFETY.md).

## Checkout and develop

```bash
git clone https://github.com/1998x-stack/USEFULL_TOOLS.git
cd USEFULL_TOOLS
python -m pip install -e ".[dev,all]"
ruff check devkit/ tests/
pytest tests/ -m "not pdf_integration and not visual_integration"
```

Use a feature branch based on current `main`. Avoid introducing a second
entry point for an existing CLI command; update its Click wrapper and Python
API consistently.

## Real document integration tests

Conversion integration needs more than pip packages. On Ubuntu:

```bash
sudo apt-get update
sudo apt-get install -y pandoc libreoffice-writer fontconfig fonts-noto-cjk
pytest tests/test_convert_v04b.py -q
pytest tests/test_pdf_v04c.py tests/test_quality_v04e.py -m pdf_integration -q
```

The screenshot golden job uses a **locked Ubuntu 24.04** environment
and approved PNG baselines. Run it using CI or a matching environment:

```bash
python -m devkit.convert.visual_cli verify \
  --manifest tests/fixtures/visual_v04d/manifest.json \
  --out-dir /tmp/visual-verify
pytest tests/test_visual_v04d.py tests/test_quality_v04e.py \
  -m visual_integration -q
```

Do **not** regenerate approved snapshots in an ordinary CI job. Use
`candidate` only to prepare review artifacts. Maintainers review page
images and diagnostics, then approve a separate commit with hashes and
the renderer/font lock. See [Visual Goldens](docs/conversion-v0.4d.md).

## Engineering conventions

- Add type annotations and concise docstrings to public APIs; support Python 3.9+.
- Keep optional imports lazy and document executable/system dependencies.
- Convert failures into explicit diagnostics; preserve existing outputs on validation failure.
- Never download remote Markdown image references during document conversion.
- Avoid committing private data, third-party font binaries, or unlicensed documents.
- Add a regression test and update documentation whenever a CLI flag or data contract changes.
- For changes to data processing, maintain [V0.3 contracts](docs/data-contracts-v0.3.md).
- For document conversion, follow [V0.4 contracts](docs/conversion-v0.4.md).

## Adding or updating a tool

1. Place implementation in the appropriate `devkit/<category>/` package.
2. Add or update the command in `devkit/cli.py` without bypassing safety checks.
3. Add targeted unit tests and, for real converters, E2E cases or golden fixtures.
4. Update both [README.md](README.md) and [README_CN.md](README_CN.md), plus relevant detailed docs.
5. Run Ruff and all relevant jobs, then open a PR against current `main`.

## Pull request checklist

- [ ] Description clearly states scope and user-visible behavior.
- [ ] Tests cover successful behavior and failure/rollback behavior.
- [ ] README examples match real CLI flags and required backends.
- [ ] Existing V0.2/V0.3 regressions remain green.
- [ ] No unreviewed golden baseline, private document or font asset has been added.

## Reporting issues

Include Python version, operating system, `devkit --version`,
the exact command and input type, expected/actual behavior, and
Pandoc/LibreOffice/font information for document conversion issues.
Attach a sanitized JSON quality report when possible; do not attach private documents.

## License

Contributions are licensed under the repository's [MIT License](LICENSE).

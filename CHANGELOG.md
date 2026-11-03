# Changelog

## [Unreleased] — main branch source changes (2026-11-03)

> V0.3 and V0.4 source features are merged, but package metadata still
> declares `0.1.0`. No new public PyPI release is implied.

### V0.4 Document Conversion Fidelity — merged PR #7

- V0.4-A: staged/validated PDF and Office output, isolated LibreOffice, pypdf migration.
- V0.4-B: Pandoc JSON/typed DocumentIR conversion and real DOCX OOXML structural golden tests.
- V0.4-C: installed CJK glyph preflight, text recall and raster integrity with a complete Pandoc reference template.
- V0.4-D: six independently reviewed PNG goldens, per-page/region diffs, pagination, font/renderer lock.
- V0.4-E: named quality profiles and machine-readable conversion audit reports.

### V0.3 Data Correctness — merged PR #2

- Strict CSV schema and per-record width validation across merge, split and CSV-to-JSON.
- Streaming JSON array-to-CSV with consistent schema checks and duplicate key rejection.
- Reversible escaped JSON paths including literal separators, backslashes, and empty objects.
- Validated JSONL merge with file and line diagnostics.
- Atomic single-file output publication with input/output alias protection.
- Staged CSV splitting that refuses to overwrite existing output parts.
- Excel-to-CSV output safety, data CLI errors, and regression tests.


### V0.2 File Safety — merged PR #1

- Safe-by-default duplicate-file and batch-rename previews.
- Collision and path checks, file safety regression tests and template protection.

## [0.1.0] - 2026-03-28

### Added
- Initial release with 27+ tools across 7 categories
- Click-based CLI with `devkit` entry point
- Document & media conversion tools (PDF merge/compress, md2pdf, md2docx, media conversion, image resize)
- Text & NLP tools (information-entropy text length, keyword extraction, Chinese sentence splitter, tokenizer)
- File management tools (duplicate finder, log search, code extractor, batch rename)
- AI/LLM utilities (token counter, prompt templates, cost calculator, model comparison)
- Data processing tools (JSON flatten/merge/query, CSV merge/split/convert, Excel to CSV)
- Web utilities (QR code generate/read, URL validation with metadata)
- Developer tools (hash tool, port finder, environment checker, git statistics)
- Bilingual documentation (English + Chinese)
- Optional dependency groups for minimal installs (`[ai]`, `[nlp]`, `[convert]`, `[data]`, `[web]`, `[all]`)
- pytest test suite with 60 tests
- MIT License

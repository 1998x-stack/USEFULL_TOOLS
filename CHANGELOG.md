# Changelog

## [Unreleased] — V0.3 Data Correctness (2026-11-03)

- Strict CSV schema and per-record width validation across merge, split and CSV-to-JSON.
- Streaming JSON array-to-CSV with consistent schema checks and duplicate key rejection.
- Reversible escaped JSON paths including literal separators, backslashes, and empty objects.
- Validated JSONL merge with file and line diagnostics.
- Atomic single-file output publication with input/output alias protection.
- Staged CSV splitting that refuses to overwrite existing output parts.
- Excel-to-CSV output safety, data CLI errors, and regression tests.


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

# Changelog

## [Unreleased] — V0.4-B Structure-aware Markdown→DOCX (2026-11-03)

- Pandoc JSON AST as the lossless rendering contract and typed DocumentIR projection.
- Unified md2docx and doc --to docx CLI pipeline with optional --reference-doc.
- Strict local-image preflight and independent DOCX structural integrity checks.
- Golden end-to-end tests for headings, paragraphs, inline formatting, links,
  nested lists, tables, media and code across Python 3.9–3.12.

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

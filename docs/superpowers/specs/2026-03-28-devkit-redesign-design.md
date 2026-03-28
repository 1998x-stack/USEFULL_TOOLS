# DevKit: Complete Project Redesign Specification

**Date:** 2026-03-28
**Status:** Draft
**Author:** Claude + User

---

## 1. Overview

Transform the current `USEFULL_TOOLS` repository from a personal scripts collection into **devkit** — a professional, pip-installable Python CLI toolkit positioned as "A Swiss Army Knife for Developers." The goal is to make this project GitHub-trending quality with clean architecture, comprehensive documentation, and genuinely useful tools.

### 1.1 Key Decisions

- **Name:** `devkit` (PyPI package name TBD based on availability, fallback: `devkit-tools`)
- **Audience:** Developers, NLP engineers, productivity hackers — broad appeal
- **Language:** Bilingual documentation (English primary, Chinese secondary)
- **Architecture:** Modular CLI toolkit using `click`, pip-installable
- **License:** MIT
- **Personal data:** All personal data files (JSON exports, ICS, CSV, logs) removed from repo

---

## 2. Project Structure

```
devkit/
├── README.md                    # Bilingual README (EN primary, CN section at bottom)
├── README_CN.md                 # Full Chinese README
├── LICENSE                      # MIT License
├── pyproject.toml               # PEP 621 packaging
├── requirements.txt             # Runtime dependencies
├── requirements-dev.txt         # Dev/test dependencies
├── .gitignore                   # Comprehensive gitignore
├── CONTRIBUTING.md              # Contribution guidelines
├── CHANGELOG.md                 # Version history
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions: lint + test
│
├── devkit/                      # Main Python package
│   ├── __init__.py              # Version, package metadata
│   ├── cli.py                   # Click-based CLI entry point
│   │
│   ├── convert/                 # Document & Media Conversion
│   │   ├── __init__.py
│   │   ├── md2pdf.py           # Markdown to PDF
│   │   ├── md2docx.py          # Markdown to DOCX
│   │   ├── pdf_merge.py        # Merge multiple PDFs
│   │   ├── pdf_compress.py     # Compress PDFs via Ghostscript
│   │   ├── pdf_parse.py        # PDF to Markdown (AI-powered)
│   │   ├── media.py            # MP4→MP3, WebP→PNG, image resize
│   │   └── doc_convert.py      # Word↔PDF/JPG/Markdown
│   │
│   ├── text/                    # Text & NLP Processing
│   │   ├── __init__.py
│   │   ├── text_length.py      # Information-entropy text length calc
│   │   ├── keywords.py         # Weighted keyword extraction (CN/EN)
│   │   ├── split_sentence.py   # Chinese sentence splitter
│   │   └── tokenizer.py        # LLM token counter
│   │
│   ├── files/                   # File Management
│   │   ├── __init__.py
│   │   ├── dedup.py            # Remove duplicate files
│   │   ├── search_log.py       # Search through log files
│   │   ├── extract_code.py     # Extract & merge source code
│   │   └── batch_rename.py     # Batch file renaming
│   │
│   ├── ai/                      # AI/LLM Utilities
│   │   ├── __init__.py
│   │   ├── token_counter.py    # Token counting for GPT/Claude/Llama
│   │   ├── prompt_template.py  # Prompt template manager
│   │   └── cost_calculator.py  # API cost estimator
│   │
│   ├── data/                    # Data Processing
│   │   ├── __init__.py
│   │   ├── json_utils.py       # JSON flatten/merge/query
│   │   ├── csv_utils.py        # CSV merge/split/convert
│   │   └── excel2csv.py        # Excel to CSV
│   │
│   ├── web/                     # Web Utilities
│   │   ├── __init__.py
│   │   ├── qr_code.py          # QR code generate/read
│   │   └── url_validator.py    # URL validation & metadata
│   │
│   ├── dev/                     # Developer Utilities
│   │   ├── __init__.py
│   │   ├── git_stats.py        # Git repo statistics
│   │   ├── port_finder.py      # Find available ports
│   │   ├── env_checker.py      # Dev environment verification
│   │   └── hash_tool.py        # File/string hashing
│   │
│   └── utils.py                 # Shared utilities
│
├── tests/
│   ├── __init__.py
│   ├── test_convert.py
│   ├── test_text.py
│   ├── test_files.py
│   ├── test_ai.py
│   ├── test_data.py
│   ├── test_web.py
│   └── test_dev.py
│
├── examples/
│   ├── sample_data/
│   │   ├── sample.md
│   │   ├── sample.csv
│   │   └── sample.json
│   └── notebooks/
│       └── demo.ipynb
│
└── docs/
    └── assets/
        └── banner.png
```

### 2.1 What Gets Removed

- `files/` directory (personal JSON exports, ICS files, CSV, log files)
- `logs/` directory
- `notion_calendar/` directory (too personal/niche for the main package)
- `tools/css-tools/` and `tools/js-tools/` (converted to Python equivalents or documented separately)
- `.DS_Store` files

### 2.2 What Gets Migrated

| Current File | New Location | Changes |
|---|---|---|
| `good_codes/calculate_text_length.py` | `devkit/text/text_length.py` | Add CLI wrapper, clean imports |
| `good_codes/weighted_keywords.py` | `devkit/text/keywords.py` | Add CLI, remove sys.path hack |
| `good_codes/lru_cache.py` | Removed | Python stdlib has this |
| `good_codes/pdf_parser.py` | `devkit/convert/pdf_parse.py` | Clean up, add CLI |
| `tools/python-tools/md2docx.py` | `devkit/convert/md2docx.py` | Remove print statements, add CLI |
| `tools/python-tools/md2pdf.py` | `devkit/convert/md2pdf.py` | Fix hardcoded paths, add CLI |
| `tools/python-tools/merge_pdf.py` | `devkit/convert/pdf_merge.py` | Remove hardcoded path, add CLI |
| `tools/python-tools/split_sents.py` | `devkit/text/split_sentence.py` | Clean up, add CLI |
| `tools/python-tools/util.py` | `devkit/utils.py` | Remove unused imports |
| `tools/bash-tools/compress_pdfs.sh` | `devkit/convert/pdf_compress.py` | Python wrapper around Ghostscript |
| `tools/bash-tools/convert_mp4_to_mp3.sh` | `devkit/convert/media.py` | Python wrapper around ffmpeg |
| `tools/bash-tools/webp2png.sh` | `devkit/convert/media.py` | Python using Pillow |
| `tools/bash-tools/resize.sh` | `devkit/convert/media.py` | Python using Pillow |
| `tools/bash-tools/remove_duplicates.sh` | `devkit/files/dedup.py` | Pure Python implementation |
| `tools/bash-tools/search_log.sh` | `devkit/files/search_log.py` | Pure Python implementation |
| `tools/bash-tools/extract_codes.sh` | `devkit/files/extract_code.py` | Pure Python implementation |

---

## 3. CLI Design

### 3.1 Entry Point

Using `click` with command groups:

```python
# devkit/cli.py
import click

@click.group()
@click.version_option()
def cli():
    """devkit - A Swiss Army Knife for Developers"""
    pass

# Sub-groups
@cli.group()
def convert():
    """Document & media conversion tools"""
    pass

@cli.group()
def text():
    """Text & NLP processing tools"""
    pass

@cli.group()
def files():
    """File management tools"""
    pass

@cli.group()
def ai():
    """AI/LLM utility tools"""
    pass

@cli.group()
def data():
    """Data processing tools"""
    pass

@cli.group()
def web():
    """Web utility tools"""
    pass

@cli.group()
def dev():
    """Developer utility tools"""
    pass
```

### 3.2 Command Reference

#### Convert Commands
```
devkit convert md2pdf <input> [-o output]
devkit convert md2docx <input> [-o output]
devkit convert pdf-merge <directory> [-o output.pdf]
devkit convert pdf-compress <input> [--quality ebook|screen|printer]
devkit convert pdf-parse <input> [-o output_dir] [--model gpt-4o]
devkit convert mp4-to-mp3 <input_or_dir>
devkit convert webp-to-png <input_or_dir>
devkit convert resize <input> <size> [-o output]
devkit convert doc <input> --to pdf|jpg|md|docx
```

#### Text Commands
```
devkit text length <text_or_file>
devkit text keywords <text_or_file> [--lang zh|en] [--mode all|filter] [--top 10]
devkit text split <text_or_file> [--criterion coarse|fine]
devkit text tokens <text_or_file> [--model gpt-4|claude-3|llama]
```

#### Files Commands
```
devkit files dedup <directory> [--extensions pdf,mp3,mp4,html]
devkit files search <file> <query> [--mode lines|chars] [--context 20]
devkit files extract-code <directory> [-o output.txt] [--extensions py,js,ts]
devkit files rename <directory> --pattern <pattern> [--dry-run]
```

#### AI Commands
```
devkit ai tokens <text_or_file> [--model gpt-4|claude-3|llama-3]
devkit ai cost --model <model> --input-tokens <n> --output-tokens <n>
devkit ai prompt <template_name> [--vars '{"key": "value"}'] [--list]
```

#### Data Commands
```
devkit data json-flatten <input> [-o output]
devkit data json-merge <files...> [-o output]
devkit data csv-merge <files...> [-o output]
devkit data csv-split <input> --rows <n> [-o output_dir]
devkit data excel2csv <input> [--sheet <name>] [-o output]
```

#### Web Commands
```
devkit web qrcode <text_or_url> [-o output.png] [--size 300]
devkit web qrcode-read <image>
devkit web validate-url <url> [--metadata]
```

#### Dev Commands
```
devkit dev git-stats [--path .] [--format table|json]
devkit dev ports [--range 3000-9000] [--count 5]
devkit dev hash <file_or_string> [--algo md5|sha256|sha512]
devkit dev env-check [--tools python,node,git,docker]
```

---

## 4. New Tools Specification

### 4.1 Token Counter (`devkit/ai/token_counter.py`)

Count tokens for text using encoding models from various LLM providers.

**Dependencies:** `tiktoken`

**Functions:**
- `count_tokens(text: str, model: str = "gpt-4") -> int`
- `count_tokens_file(file_path: str, model: str = "gpt-4") -> int`
- `supported_models() -> list[str]`

**Supported models:** GPT-4, GPT-3.5, Claude (cl100k approximation), Llama (sentencepiece approximation)

### 4.2 Prompt Template (`devkit/ai/prompt_template.py`)

Manage and render prompt templates with Jinja2 variables.

**Dependencies:** `jinja2`

**Functions:**
- `render_template(template: str, variables: dict) -> str`
- `load_template(name: str) -> str` — loads from `~/.devkit/prompts/`
- `list_templates() -> list[str]`
- `save_template(name: str, content: str)`

### 4.3 API Cost Calculator (`devkit/ai/cost_calculator.py`)

Estimate API costs for different LLM providers.

**Dependencies:** None (pure Python, hardcoded pricing)

**Functions:**
- `calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float`
- `compare_costs(input_tokens: int, output_tokens: int) -> dict` — compare across providers
- `supported_models() -> list[str]`

**Supported providers:** OpenAI (GPT-4o, GPT-4, GPT-3.5), Anthropic (Claude Opus, Sonnet, Haiku), Google (Gemini Pro, Flash)

### 4.4 JSON Utils (`devkit/data/json_utils.py`)

**Functions:**
- `flatten_json(data: dict, separator: str = ".") -> dict`
- `unflatten_json(data: dict, separator: str = ".") -> dict`
- `merge_jsonl(files: list[str], output: str)`
- `json_query(data: dict, path: str) -> Any` — simple dot-notation query

### 4.5 CSV Utils (`devkit/data/csv_utils.py`)

**Functions:**
- `merge_csvs(files: list[str], output: str)`
- `split_csv(file: str, rows_per_file: int, output_dir: str)`
- `csv_to_json(file: str, output: str)`
- `json_to_csv(file: str, output: str)`

### 4.6 Excel to CSV (`devkit/data/excel2csv.py`)

**Dependencies:** `openpyxl`

**Functions:**
- `excel_to_csv(file: str, output: str, sheet: str | None = None)`
- `list_sheets(file: str) -> list[str]`

### 4.7 QR Code (`devkit/web/qr_code.py`)

**Dependencies:** `qrcode`, `Pillow`, `pyzbar`

**Functions:**
- `generate_qr(data: str, output: str, size: int = 300)`
- `read_qr(image_path: str) -> str`

### 4.8 URL Validator (`devkit/web/url_validator.py`)

**Dependencies:** `requests`, `beautifulsoup4`

**Functions:**
- `is_valid_url(url: str) -> bool`
- `get_metadata(url: str) -> dict` — returns title, description, status code

### 4.9 Git Stats (`devkit/dev/git_stats.py`)

**Dependencies:** None (uses `subprocess` with `git`)

**Functions:**
- `get_stats(path: str = ".") -> dict` — total commits, contributors, LOC, file types
- `top_contributors(path: str, n: int = 10) -> list`
- `commit_frequency(path: str, days: int = 30) -> dict`

### 4.10 Port Finder (`devkit/dev/port_finder.py`)

**Dependencies:** None (uses `socket`)

**Functions:**
- `find_available_ports(start: int = 3000, end: int = 9000, count: int = 5) -> list[int]`
- `is_port_available(port: int) -> bool`

### 4.11 Hash Tool (`devkit/dev/hash_tool.py`)

**Dependencies:** None (uses `hashlib`)

**Functions:**
- `hash_string(text: str, algo: str = "sha256") -> str`
- `hash_file(path: str, algo: str = "sha256") -> str`

### 4.12 Env Checker (`devkit/dev/env_checker.py`)

**Dependencies:** None (uses `subprocess`, `shutil`)

**Functions:**
- `check_environment(tools: list[str] = None) -> dict` — checks Python, Node, Git, Docker, ffmpeg, etc.
- `print_report(results: dict)` — pretty-print the check results

### 4.13 Batch Rename (`devkit/files/batch_rename.py`)

**Dependencies:** None

**Functions:**
- `batch_rename(directory: str, pattern: str, dry_run: bool = True) -> list[tuple[str, str]]`
- Supports `{n}`, `{name}`, `{ext}`, `{date}` placeholders

---

## 5. README Design

### 5.1 Top Section

```markdown
<div align="center">
  <h1>devkit</h1>
  <p><strong>A Swiss Army Knife for Developers</strong></p>
  <p>27+ ready-to-use CLI tools for file conversion, text processing, AI/LLM, data handling, and more.</p>

  [PyPI badge] [Python badge] [License badge] [Stars badge] [CI badge]
</div>
```

### 5.2 Features Table

Visual emoji-based table showing all 7 categories with tool counts.

### 5.3 Quick Start

```markdown
## Quick Start

pip install devkit-tools

# Convert Markdown to PDF
devkit convert md2pdf README.md

# Count tokens for GPT-4
devkit text tokens "Hello world" --model gpt-4

# Find available ports
devkit dev ports --range 3000-9000
```

### 5.4 Tool Categories

Each category gets a collapsible `<details>` section with:
- Category description
- Table of all tools with name, description, and example command
- Link to detailed documentation

### 5.5 Chinese Section

Full Chinese translation at the bottom under `---` separator, or link to `README_CN.md`.

---

## 6. Packaging & Distribution

### 6.1 pyproject.toml

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "devkit-tools"
version = "0.1.0"
description = "A Swiss Army Knife for Developers - 27+ CLI tools"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.9"
authors = [{name = "Your Name"}]
keywords = ["cli", "tools", "developer", "utilities", "converter"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Topic :: Utilities",
]

[project.scripts]
devkit = "devkit.cli:cli"

[project.optional-dependencies]
ai = ["tiktoken", "jinja2"]
nlp = ["jieba", "jionlp"]
convert = ["PyMuPDF", "python-docx", "markdown", "beautifulsoup4", "reportlab", "Pillow"]
data = ["openpyxl"]
web = ["qrcode", "pyzbar", "requests", "beautifulsoup4"]
all = ["devkit-tools[ai,nlp,convert,data,web]"]
```

### 6.2 Optional Dependencies Strategy

Core tools (files, dev, utils) have zero dependencies. Feature-specific tools use optional dependency groups:
- `pip install devkit-tools` — core tools only
- `pip install devkit-tools[ai]` — + AI/LLM tools
- `pip install devkit-tools[all]` — everything

---

## 7. Code Quality Standards

### 7.1 Every Module Must Have

- Type hints on all function signatures
- Docstrings (English, with Chinese translations where helpful for CJK-specific tools)
- A `if __name__ == "__main__"` block that can run standalone
- CLI integration via click command registration
- No hardcoded paths or personal data

### 7.2 Code Cleanup Rules for Migrated Code

- Remove all `print()` statements — use `click.echo()` in CLI, `logging` in library code
- Remove `sys.path.append` hacks
- Remove hardcoded personal paths
- Replace Chinese-only variable names with English
- Add consistent error handling with user-friendly messages
- Remove the duplicate `lru_cache` implementation (stdlib has this)

### 7.3 Testing

- pytest-based test suite
- Each module has corresponding test file
- Tests use fixture data from `examples/sample_data/`
- CI runs tests on Python 3.9, 3.10, 3.11, 3.12

---

## 8. Migration Plan Summary

### Phase 1: Setup
- Create new directory structure
- Set up pyproject.toml, requirements, .gitignore, LICENSE
- Create CLI skeleton

### Phase 2: Migrate Existing Tools
- Move and clean up each existing tool
- Wire up CLI commands
- Write tests for migrated code

### Phase 3: Add New Tools
- Implement 13 new tools
- Wire up CLI commands
- Write tests

### Phase 4: Documentation
- Write README.md (bilingual)
- Write CONTRIBUTING.md
- Create example data and notebooks
- Write CHANGELOG.md

### Phase 5: Polish
- GitHub Actions CI
- Final review and cleanup
- Remove old file structure
- Tag v0.1.0

---

## 9. Success Criteria

- All 27+ tools work via CLI and as importable modules
- `pip install devkit-tools` works cleanly
- All tests pass
- README is comprehensive, bilingual, and visually appealing
- No personal data in the repository
- CI passes on push
- Code follows consistent patterns throughout

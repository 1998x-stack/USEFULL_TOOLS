# DevKit Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform USEFULL_TOOLS into `devkit` — a pip-installable Python CLI toolkit with 27+ tools across 7 categories.

**Architecture:** Click-based CLI with lazy-loaded subcommand groups. Each tool category is a Python subpackage with `__init__.py` re-exports. Optional dependency groups let users install only what they need. All tools work both as CLI commands and importable library functions.

**Tech Stack:** Python 3.9+, Click (CLI), pytest (testing), setuptools (packaging). Optional: tiktoken, jieba, PyMuPDF, Pillow, openpyxl, qrcode, requests, beautifulsoup4, jinja2.

**Spec:** `docs/superpowers/specs/2026-03-28-devkit-redesign-design.md`

---

## File Structure

```
devkit/                          # Python package root
├── __init__.py                  # Version string
├── cli.py                       # Click CLI entry + all subcommand groups
├── utils.py                     # Shared utilities (URL, JSON, UUID, time)
├── convert/
│   ├── __init__.py
│   ├── md2pdf.py
│   ├── md2docx.py
│   ├── pdf_merge.py
│   ├── pdf_compress.py
│   ├── pdf_parse.py
│   ├── media.py
│   └── doc_convert.py
├── text/
│   ├── __init__.py
│   ├── text_length.py
│   ├── keywords.py
│   ├── split_sentence.py
│   └── tokenizer.py
├── files/
│   ├── __init__.py
│   ├── dedup.py
│   ├── search_log.py
│   ├── extract_code.py
│   └── batch_rename.py
├── ai/
│   ├── __init__.py
│   ├── token_counter.py
│   ├── prompt_template.py
│   └── cost_calculator.py
├── data/
│   ├── __init__.py
│   ├── json_utils.py
│   ├── csv_utils.py
│   └── excel2csv.py
├── web/
│   ├── __init__.py
│   ├── qr_code.py
│   └── url_validator.py
└── dev/
    ├── __init__.py
    ├── git_stats.py
    ├── port_finder.py
    ├── env_checker.py
    └── hash_tool.py

tests/
├── __init__.py
├── test_utils.py
├── test_text.py
├── test_files.py
├── test_ai.py
├── test_data.py
├── test_web.py
├── test_dev.py
└── test_cli.py

examples/sample_data/
├── sample.md
├── sample.csv
└── sample.json

Root files:
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── LICENSE
├── .gitignore
├── CONTRIBUTING.md
├── CHANGELOG.md
├── README.md
├── README_CN.md
└── .github/workflows/ci.yml
```

---

## Task 1: Project Scaffolding & Packaging

**Files:**
- Create: `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, `LICENSE`, `.gitignore` (replace), `devkit/__init__.py`, `devkit/cli.py`, `tests/__init__.py`, `examples/sample_data/sample.md`, `examples/sample_data/sample.csv`, `examples/sample_data/sample.json`

- [ ] **Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "devkit-tools"
version = "0.1.0"
description = "A Swiss Army Knife for Developers - 27+ CLI tools for file conversion, text processing, AI/LLM, and more"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.9"
authors = [{name = "1998x-stack", email = "2484230700@qq.com"}]
keywords = ["cli", "tools", "developer", "utilities", "converter", "nlp", "ai", "devops"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Utilities",
    "Topic :: Software Development :: Libraries :: Python Modules",
]
dependencies = [
    "click>=8.0",
]

[project.scripts]
devkit = "devkit.cli:cli"

[project.urls]
Homepage = "https://github.com/1998x-stack/devkit"
Repository = "https://github.com/1998x-stack/devkit"
Issues = "https://github.com/1998x-stack/devkit/issues"

[project.optional-dependencies]
ai = ["tiktoken>=0.5.0", "jinja2>=3.0"]
nlp = ["jieba>=0.42", "jionlp>=1.4"]
convert = ["PyMuPDF>=1.23", "python-docx>=0.8", "markdown>=3.4", "beautifulsoup4>=4.12", "reportlab>=4.0", "Pillow>=10.0", "markdown2>=2.4", "PyPDF2>=3.0"]
data = ["openpyxl>=3.1"]
web = ["qrcode[pil]>=7.4", "requests>=2.28", "beautifulsoup4>=4.12"]
all = ["devkit-tools[ai,nlp,convert,data,web]"]
dev = ["pytest>=7.0", "pytest-cov>=4.0", "ruff>=0.1.0"]

[tool.setuptools.packages.find]
include = ["devkit*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"

[tool.ruff]
target-version = "py39"
line-length = 120
```

- [ ] **Step 2: Create requirements.txt**

```
click>=8.0
```

- [ ] **Step 3: Create requirements-dev.txt**

```
pytest>=7.0
pytest-cov>=4.0
ruff>=0.1.0
```

- [ ] **Step 4: Create MIT LICENSE**

```
MIT License

Copyright (c) 2026 1998x-stack

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 5: Replace .gitignore with comprehensive version**

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
*.egg-info/
dist/
build/
*.egg
.eggs/

# Virtual environments
venv/
.venv/
env/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/

# Project-specific
logs/
data/
ics_files/
*.ics
*.log

# Distribution
*.tar.gz
*.whl
```

- [ ] **Step 6: Create devkit/__init__.py**

```python
"""devkit - A Swiss Army Knife for Developers."""

__version__ = "0.1.0"
```

- [ ] **Step 7: Create CLI skeleton at devkit/cli.py**

```python
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
```

- [ ] **Step 8: Create tests/__init__.py (empty) and test_cli.py**

```python
# tests/__init__.py
```

```python
# tests/test_cli.py
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
```

- [ ] **Step 9: Create sample data files**

`examples/sample_data/sample.md`:
```markdown
# Sample Document

This is a **sample** markdown document for testing devkit tools.

## Features

- Bullet point one
- Bullet point two

## Code Example

```python
def hello():
    return "Hello, World!"
```

## Math

The equation $E = mc^2$ is famous.

---

*End of sample document.*
```

`examples/sample_data/sample.csv`:
```csv
name,age,city,score
Alice,30,Beijing,95.5
Bob,25,Shanghai,88.0
Charlie,35,Shenzhen,92.3
Diana,28,Guangzhou,97.1
Eve,32,Hangzhou,85.6
```

`examples/sample_data/sample.json`:
```json
{
  "name": "devkit",
  "version": "0.1.0",
  "features": {
    "convert": ["md2pdf", "md2docx", "pdf-merge"],
    "text": ["length", "keywords", "split"],
    "ai": ["tokens", "cost", "prompt"]
  },
  "metadata": {
    "author": {
      "name": "1998x-stack",
      "location": "China"
    },
    "tags": ["cli", "tools", "developer"]
  }
}
```

- [ ] **Step 10: Create all __init__.py files for subpackages**

Create empty `__init__.py` in each: `devkit/convert/`, `devkit/text/`, `devkit/files/`, `devkit/ai/`, `devkit/data/`, `devkit/web/`, `devkit/dev/`.

- [ ] **Step 11: Install package in dev mode and run tests**

Run:
```bash
cd /Users/mx/Desktop/series/项目系列/USEFULL_TOOLS
pip install -e ".[dev]"
pytest tests/test_cli.py -v
```
Expected: All 3 tests pass.

- [ ] **Step 12: Commit**

```bash
git add pyproject.toml requirements.txt requirements-dev.txt LICENSE .gitignore devkit/ tests/ examples/
git commit -m "feat: project scaffolding with CLI skeleton, packaging, and test infrastructure"
```

---

## Task 2: Shared Utilities Module

**Files:**
- Create: `devkit/utils.py`
- Test: `tests/test_utils.py`

Migrates from `tools/python-tools/util.py`. Removes unused imports, personal paths, and `demjson3` dependency.

- [ ] **Step 1: Write tests for utils**

```python
# tests/test_utils.py
"""Test shared utilities."""

import json
import os
import tempfile
from datetime import datetime

from devkit.utils import (
    is_valid_url,
    parse_json,
    json_dumps,
    json_loads,
    create_uuid_from_string,
    deduplicate,
)


def test_is_valid_url_valid():
    assert is_valid_url("https://example.com") is True
    assert is_valid_url("http://example.com/path?q=1") is True


def test_is_valid_url_invalid():
    assert is_valid_url("not-a-url") is False
    assert is_valid_url("") is False
    assert is_valid_url("ftp://") is False


def test_parse_json_valid():
    result = parse_json('{"key": "value", "num": 42}')
    assert result == {"key": "value", "num": 42}


def test_parse_json_invalid():
    result = parse_json("not json")
    assert result is None


def test_json_dumps_with_datetime():
    data = {"time": datetime(2026, 1, 1, 12, 0)}
    result = json_dumps(data)
    assert "2026-01-01T12:00:00" in result


def test_json_dumps_chinese():
    data = {"name": "你好"}
    result = json_dumps(data)
    assert "你好" in result  # ensure_ascii=False


def test_json_loads():
    result = json_loads('{"key": "value"}')
    assert result == {"key": "value"}


def test_create_uuid_deterministic():
    uuid1 = create_uuid_from_string("test")
    uuid2 = create_uuid_from_string("test")
    assert uuid1 == uuid2


def test_create_uuid_different_inputs():
    uuid1 = create_uuid_from_string("test1")
    uuid2 = create_uuid_from_string("test2")
    assert uuid1 != uuid2


def test_deduplicate():
    assert deduplicate([1, 2, 3, 2, 1]) == [1, 2, 3]


def test_deduplicate_preserves_order():
    assert deduplicate([3, 1, 2, 1, 3]) == [3, 1, 2]


def test_deduplicate_empty():
    assert deduplicate([]) == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_utils.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'devkit.utils'` (file doesn't exist yet with these functions)

- [ ] **Step 3: Implement devkit/utils.py**

```python
"""Shared utility functions for devkit."""

import hashlib
import json
import uuid
from datetime import datetime
from typing import Any, Optional
from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    """Check if a string is a valid URL.

    Args:
        url: String to validate.

    Returns:
        True if the string is a valid URL with scheme and netloc.
    """
    if not url:
        return False
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except ValueError:
        return False


def parse_json(string: str) -> Optional[dict]:
    """Parse a JSON string, returning None on failure.

    Args:
        string: JSON string to parse.

    Returns:
        Parsed dict or None if parsing fails.
    """
    try:
        return json_loads(string)
    except (json.JSONDecodeError, TypeError, ValueError):
        return None


def json_dumps(data: Any, indent: int = 2) -> str:
    """Serialize data to JSON string with datetime support.

    Args:
        data: Data to serialize.
        indent: Indentation level.

    Returns:
        JSON string.
    """
    def safe_serializer(obj: Any) -> str:
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    return json.dumps(data, indent=indent, default=safe_serializer, ensure_ascii=False)


def json_loads(data: str) -> Any:
    """Parse JSON string with relaxed parsing.

    Args:
        data: JSON string.

    Returns:
        Parsed object.
    """
    return json.loads(data, strict=False)


def create_uuid_from_string(val: str) -> uuid.UUID:
    """Generate a deterministic UUID from a string using MD5 hashing.

    Args:
        val: Input string.

    Returns:
        UUID derived from the string.
    """
    hex_string = hashlib.md5(val.encode("UTF-8")).hexdigest()
    return uuid.UUID(hex=hex_string)


def deduplicate(target_list: list) -> list:
    """Remove duplicates from a list while preserving order.

    Args:
        target_list: List with potential duplicates.

    Returns:
        Deduplicated list.
    """
    seen = set()
    result = []
    for item in target_list:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_utils.py -v`
Expected: All 11 tests pass.

- [ ] **Step 5: Commit**

```bash
git add devkit/utils.py tests/test_utils.py
git commit -m "feat: add shared utilities module (URL validation, JSON, UUID, dedup)"
```

---

## Task 3: Dev Module (Zero Dependencies)

**Files:**
- Create: `devkit/dev/hash_tool.py`, `devkit/dev/port_finder.py`, `devkit/dev/env_checker.py`, `devkit/dev/git_stats.py`
- Modify: `devkit/cli.py` (add dev commands)
- Test: `tests/test_dev.py`

Starting with zero-dependency modules to build out the pattern before tackling modules with heavy deps.

- [ ] **Step 1: Write tests**

```python
# tests/test_dev.py
"""Tests for developer utility tools."""

import os
import socket
import tempfile

from devkit.dev.hash_tool import hash_string, hash_file
from devkit.dev.port_finder import is_port_available, find_available_ports
from devkit.dev.env_checker import check_environment
from devkit.dev.git_stats import get_stats


# --- hash_tool tests ---

def test_hash_string_sha256():
    result = hash_string("hello", algo="sha256")
    assert result == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_hash_string_md5():
    result = hash_string("hello", algo="md5")
    assert result == "5d41402abc4b2a76b9719d911017c592"


def test_hash_file(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("hello")
    result = hash_file(str(f), algo="sha256")
    assert result == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_hash_file_not_found():
    result = hash_file("/nonexistent/file.txt")
    assert result is None


# --- port_finder tests ---

def test_is_port_available():
    # Port 0 lets OS pick a free port, so high ports are usually free
    result = is_port_available(58932)
    assert isinstance(result, bool)


def test_find_available_ports():
    ports = find_available_ports(start=49152, end=49200, count=3)
    assert isinstance(ports, list)
    assert len(ports) <= 3
    for port in ports:
        assert 49152 <= port <= 49200


# --- env_checker tests ---

def test_check_environment_python():
    results = check_environment(tools=["python"])
    assert "python" in results
    assert results["python"]["found"] is True
    assert "version" in results["python"]


def test_check_environment_nonexistent():
    results = check_environment(tools=["nonexistent_tool_xyz"])
    assert "nonexistent_tool_xyz" in results
    assert results["nonexistent_tool_xyz"]["found"] is False


# --- git_stats tests ---

def test_get_stats_current_repo():
    # We're inside a git repo, so this should work
    stats = get_stats(".")
    assert "total_commits" in stats
    assert "contributors" in stats
    assert isinstance(stats["total_commits"], int)
    assert stats["total_commits"] > 0


def test_get_stats_invalid_path():
    stats = get_stats("/tmp/not_a_git_repo_xyz")
    assert stats.get("error") is not None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_dev.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement devkit/dev/hash_tool.py**

```python
"""File and string hashing utility."""

import hashlib
from typing import Optional


SUPPORTED_ALGORITHMS = ["md5", "sha1", "sha256", "sha512"]


def hash_string(text: str, algo: str = "sha256") -> str:
    """Hash a string using the specified algorithm.

    Args:
        text: String to hash.
        algo: Hash algorithm (md5, sha1, sha256, sha512).

    Returns:
        Hex digest string.
    """
    h = hashlib.new(algo)
    h.update(text.encode("utf-8"))
    return h.hexdigest()


def hash_file(path: str, algo: str = "sha256") -> Optional[str]:
    """Hash a file using the specified algorithm.

    Args:
        path: Path to the file.
        algo: Hash algorithm (md5, sha1, sha256, sha512).

    Returns:
        Hex digest string, or None if file not found.
    """
    try:
        h = hashlib.new(algo)
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except FileNotFoundError:
        return None
```

- [ ] **Step 4: Implement devkit/dev/port_finder.py**

```python
"""Find available network ports."""

import socket
from typing import List


def is_port_available(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a port is available for binding.

    Args:
        port: Port number to check.
        host: Host to bind to.

    Returns:
        True if the port is available.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((host, port))
            return True
        except OSError:
            return False


def find_available_ports(
    start: int = 3000, end: int = 9000, count: int = 5, host: str = "127.0.0.1"
) -> List[int]:
    """Find available ports in a range.

    Args:
        start: Start of port range (inclusive).
        end: End of port range (inclusive).
        count: Number of ports to find.
        host: Host to bind to.

    Returns:
        List of available port numbers.
    """
    available = []
    for port in range(start, end + 1):
        if is_port_available(port, host):
            available.append(port)
            if len(available) >= count:
                break
    return available
```

- [ ] **Step 5: Implement devkit/dev/env_checker.py**

```python
"""Check development environment for required tools."""

import shutil
import subprocess
from typing import Dict, List, Optional


DEFAULT_TOOLS = ["python", "python3", "pip", "git", "node", "npm", "docker", "ffmpeg"]


def _get_version(tool: str) -> Optional[str]:
    """Get version string for a tool."""
    version_flags = {"python": "--version", "python3": "--version", "pip": "--version",
                     "git": "--version", "node": "--version", "npm": "--version",
                     "docker": "--version", "ffmpeg": "-version", "java": "-version",
                     "go": "version", "rustc": "--version", "cargo": "--version"}
    flag = version_flags.get(tool, "--version")
    try:
        result = subprocess.run(
            [tool, flag], capture_output=True, text=True, timeout=5
        )
        output = result.stdout.strip() or result.stderr.strip()
        return output.split("\n")[0] if output else "installed"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def check_environment(tools: Optional[List[str]] = None) -> Dict[str, dict]:
    """Check if development tools are installed and get their versions.

    Args:
        tools: List of tool names to check. Defaults to common dev tools.

    Returns:
        Dict mapping tool name to {found: bool, version: str, path: str}.
    """
    if tools is None:
        tools = DEFAULT_TOOLS

    results = {}
    for tool in tools:
        path = shutil.which(tool)
        if path:
            version = _get_version(tool)
            results[tool] = {"found": True, "version": version or "unknown", "path": path}
        else:
            results[tool] = {"found": False, "version": None, "path": None}
    return results


def format_report(results: Dict[str, dict]) -> str:
    """Format environment check results as a readable string.

    Args:
        results: Output from check_environment().

    Returns:
        Formatted report string.
    """
    lines = ["Development Environment Check", "=" * 40]
    for tool, info in results.items():
        status = "OK" if info["found"] else "MISSING"
        version = info.get("version", "") or ""
        lines.append(f"  [{status:>7}] {tool:<12} {version}")
    found = sum(1 for v in results.values() if v["found"])
    lines.append(f"\n{found}/{len(results)} tools found.")
    return "\n".join(lines)
```

- [ ] **Step 6: Implement devkit/dev/git_stats.py**

```python
"""Git repository statistics."""

import os
import subprocess
from typing import Dict, List, Optional


def _run_git(args: List[str], cwd: str = ".") -> Optional[str]:
    """Run a git command and return stdout."""
    try:
        result = subprocess.run(
            ["git"] + args, capture_output=True, text=True, cwd=cwd, timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def get_stats(path: str = ".") -> dict:
    """Get repository statistics.

    Args:
        path: Path to the git repository.

    Returns:
        Dict with total_commits, contributors, file_count, and top file types.
    """
    if not os.path.isdir(path):
        return {"error": f"Directory not found: {path}"}

    commit_count = _run_git(["rev-list", "--count", "HEAD"], cwd=path)
    if commit_count is None:
        return {"error": f"Not a git repository: {path}"}

    contributors_raw = _run_git(["shortlog", "-sn", "--all", "--no-merges"], cwd=path)
    contributors = []
    if contributors_raw:
        for line in contributors_raw.split("\n"):
            line = line.strip()
            if line:
                parts = line.split("\t", 1)
                if len(parts) == 2:
                    contributors.append({"commits": int(parts[0].strip()), "name": parts[1].strip()})

    file_count_raw = _run_git(["ls-files"], cwd=path)
    file_count = len(file_count_raw.split("\n")) if file_count_raw else 0

    return {
        "total_commits": int(commit_count),
        "contributors": contributors,
        "file_count": file_count,
    }


def top_contributors(path: str = ".", n: int = 10) -> List[dict]:
    """Get top N contributors by commit count.

    Args:
        path: Path to the git repository.
        n: Number of top contributors to return.

    Returns:
        List of dicts with name and commits.
    """
    stats = get_stats(path)
    if "error" in stats:
        return []
    return stats["contributors"][:n]


def commit_frequency(path: str = ".", days: int = 30) -> Dict[str, int]:
    """Get commit count per day for the last N days.

    Args:
        path: Path to the git repository.
        days: Number of days to look back.

    Returns:
        Dict mapping date strings to commit counts.
    """
    raw = _run_git(
        ["log", f"--since={days} days ago", "--format=%cd", "--date=short"],
        cwd=path,
    )
    if not raw:
        return {}

    freq: Dict[str, int] = {}
    for date in raw.split("\n"):
        date = date.strip()
        if date:
            freq[date] = freq.get(date, 0) + 1
    return freq
```

- [ ] **Step 7: Update devkit/dev/__init__.py**

```python
"""Developer utility tools."""

from devkit.dev.hash_tool import hash_string, hash_file
from devkit.dev.port_finder import is_port_available, find_available_ports
from devkit.dev.env_checker import check_environment, format_report
from devkit.dev.git_stats import get_stats, top_contributors, commit_frequency
```

- [ ] **Step 8: Add dev CLI commands to devkit/cli.py**

Add these imports and commands after the `dev` group definition in `devkit/cli.py`:

```python
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
```

- [ ] **Step 9: Run tests**

Run: `pytest tests/test_dev.py -v`
Expected: All tests pass.

- [ ] **Step 10: Commit**

```bash
git add devkit/dev/ tests/test_dev.py devkit/cli.py
git commit -m "feat: add dev tools module (hash, ports, env-check, git-stats)"
```

---

## Task 4: Files Module (Zero Dependencies)

**Files:**
- Create: `devkit/files/dedup.py`, `devkit/files/search_log.py`, `devkit/files/extract_code.py`, `devkit/files/batch_rename.py`
- Modify: `devkit/cli.py`
- Test: `tests/test_files.py`

- [ ] **Step 1: Write tests**

```python
# tests/test_files.py
"""Tests for file management tools."""

import os
import tempfile

from devkit.files.dedup import find_duplicates, remove_duplicates
from devkit.files.search_log import search_file
from devkit.files.extract_code import extract_code_files
from devkit.files.batch_rename import batch_rename


# --- dedup tests ---

def test_find_duplicates(tmp_path):
    # Create original and duplicate
    (tmp_path / "file.txt").write_text("content")
    (tmp_path / "file (1).txt").write_text("duplicate")
    dups = find_duplicates(str(tmp_path), extensions=["*.txt"])
    assert len(dups) == 1
    assert "file (1).txt" in dups[0]


def test_find_duplicates_no_dupes(tmp_path):
    (tmp_path / "file.txt").write_text("content")
    dups = find_duplicates(str(tmp_path), extensions=["*.txt"])
    assert len(dups) == 0


# --- search_log tests ---

def test_search_file(tmp_path):
    log_file = tmp_path / "test.log"
    log_file.write_text("line 1\nline 2\nerror found here\nline 4\n")
    results = search_file(str(log_file), "error")
    assert len(results) > 0
    assert any("error found here" in r["line"] for r in results)


def test_search_file_not_found():
    results = search_file("/nonexistent/file.log", "test")
    assert results == []


# --- extract_code tests ---

def test_extract_code_files(tmp_path):
    (tmp_path / "app.py").write_text("print('hello')")
    (tmp_path / "style.css").write_text("body { color: red; }")
    (tmp_path / "notes.txt").write_text("not code")
    result = extract_code_files(str(tmp_path), extensions=["py", "css"])
    assert "app.py" in result
    assert "print('hello')" in result
    assert "notes.txt" not in result


# --- batch_rename tests ---

def test_batch_rename_dry_run(tmp_path):
    (tmp_path / "photo1.jpg").write_text("")
    (tmp_path / "photo2.jpg").write_text("")
    renames = batch_rename(str(tmp_path), pattern="img_{n:03d}.jpg", dry_run=True)
    assert len(renames) == 2
    assert renames[0][1].endswith("img_001.jpg")
    # Verify files NOT actually renamed (dry run)
    assert (tmp_path / "photo1.jpg").exists()


def test_batch_rename_execute(tmp_path):
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    renames = batch_rename(str(tmp_path), pattern="file_{n:02d}.txt", dry_run=False)
    assert len(renames) == 2
    assert (tmp_path / "file_01.txt").exists()
    assert (tmp_path / "file_02.txt").exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_files.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement devkit/files/dedup.py**

```python
"""Remove duplicate files based on naming patterns."""

import os
import re
from typing import List, Optional


DUPLICATE_PATTERN = re.compile(r"\((\d+)\)(\.[a-zA-Z0-9]+)$")


def find_duplicates(
    directory: str, extensions: Optional[List[str]] = None
) -> List[str]:
    """Find duplicate files matching pattern 'name (N).ext'.

    Args:
        directory: Directory to search.
        extensions: Glob patterns to filter (e.g., ['*.pdf', '*.mp3']).

    Returns:
        List of duplicate file paths.
    """
    if extensions is None:
        extensions = ["*.html", "*.pdf", "*.mp3", "*.mp4"]

    ext_set = {e.lstrip("*.") for e in extensions}
    duplicates = []

    for root, _, files in os.walk(directory):
        for filename in files:
            file_ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
            if ext_set and file_ext not in ext_set:
                continue

            match = DUPLICATE_PATTERN.search(filename)
            if match:
                # Reconstruct the original filename
                base = DUPLICATE_PATTERN.sub(match.group(2), filename)
                original = os.path.join(root, base)
                if os.path.exists(original):
                    duplicates.append(os.path.join(root, filename))

    return duplicates


def remove_duplicates(
    directory: str, extensions: Optional[List[str]] = None, dry_run: bool = True
) -> List[str]:
    """Remove duplicate files.

    Args:
        directory: Directory to search.
        extensions: Glob patterns to filter.
        dry_run: If True, only list duplicates without deleting.

    Returns:
        List of removed (or would-be-removed) file paths.
    """
    duplicates = find_duplicates(directory, extensions)
    if not dry_run:
        for filepath in duplicates:
            os.remove(filepath)
    return duplicates
```

- [ ] **Step 4: Implement devkit/files/search_log.py**

```python
"""Search through log files."""

import os
from typing import List, Optional


def search_file(
    filepath: str,
    query: str,
    context_lines: int = 3,
    max_results: int = 50,
) -> List[dict]:
    """Search for a string in a file and return matching lines with context.

    Args:
        filepath: Path to the file to search.
        query: String to search for.
        context_lines: Number of lines before/after match to include.
        max_results: Maximum number of results to return.

    Returns:
        List of dicts with line_number, line, and context.
    """
    if not os.path.isfile(filepath):
        return []

    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except (PermissionError, OSError):
        return []

    results = []
    for i, line in enumerate(lines):
        if query in line:
            start = max(0, i - context_lines)
            end = min(len(lines), i + context_lines + 1)
            context = [ln.rstrip("\n") for ln in lines[start:end]]
            results.append({
                "line_number": i + 1,
                "line": line.rstrip("\n"),
                "context": context,
            })
            if len(results) >= max_results:
                break

    return results
```

- [ ] **Step 5: Implement devkit/files/extract_code.py**

```python
"""Extract and merge source code files."""

import os
from typing import List, Optional

DEFAULT_EXTENSIONS = ["py", "js", "ts", "html", "css", "java", "go", "rs", "c", "cpp", "h"]

LANG_MAP = {
    "py": "python", "js": "javascript", "ts": "typescript",
    "html": "html", "css": "css", "java": "java", "go": "go",
    "rs": "rust", "c": "c", "cpp": "cpp", "h": "c",
    "sh": "bash", "rb": "ruby", "php": "php", "swift": "swift",
}


def extract_code_files(
    directory: str,
    extensions: Optional[List[str]] = None,
    output: Optional[str] = None,
) -> str:
    """Extract code files from a directory into a single document.

    Args:
        directory: Directory to scan.
        extensions: File extensions to include (without dots).
        output: Optional output file path.

    Returns:
        Merged content as string.
    """
    if extensions is None:
        extensions = DEFAULT_EXTENSIONS

    ext_set = set(extensions)
    parts = []

    for root, _, files in os.walk(directory):
        for filename in sorted(files):
            ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
            if ext not in ext_set:
                continue
            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, directory)
            lang = LANG_MAP.get(ext, "")

            try:
                with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except (PermissionError, OSError):
                continue

            parts.append(f"{rel_path}\n```{lang}\n{content}\n```\n")

    result = "\n".join(parts)

    if output:
        os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)

    return result
```

- [ ] **Step 6: Implement devkit/files/batch_rename.py**

```python
"""Batch file renaming with pattern templates."""

import os
import re
from datetime import datetime
from typing import List, Optional, Tuple


def batch_rename(
    directory: str,
    pattern: str,
    filter_ext: Optional[str] = None,
    dry_run: bool = True,
) -> List[Tuple[str, str]]:
    """Rename files in a directory using a pattern template.

    Supported placeholders:
        {n} or {n:03d} - Sequential number
        {name} - Original filename without extension
        {ext} - Original extension
        {date} - Current date (YYYY-MM-DD)

    Args:
        directory: Directory containing files to rename.
        pattern: New filename pattern with placeholders.
        filter_ext: Only rename files with this extension.
        dry_run: If True, return planned renames without executing.

    Returns:
        List of (old_path, new_path) tuples.
    """
    if not os.path.isdir(directory):
        return []

    files = sorted(os.listdir(directory))
    files = [f for f in files if os.path.isfile(os.path.join(directory, f))]
    if filter_ext:
        files = [f for f in files if f.endswith(f".{filter_ext}")]

    renames = []
    today = datetime.now().strftime("%Y-%m-%d")

    for i, filename in enumerate(files, start=1):
        name, ext = os.path.splitext(filename)
        ext = ext.lstrip(".")

        new_name = pattern.format(n=i, name=name, ext=ext, date=today)
        old_path = os.path.join(directory, filename)
        new_path = os.path.join(directory, new_name)
        renames.append((old_path, new_path))

    if not dry_run:
        for old_path, new_path in renames:
            os.rename(old_path, new_path)

    return renames
```

- [ ] **Step 7: Update devkit/files/__init__.py**

```python
"""File management tools."""

from devkit.files.dedup import find_duplicates, remove_duplicates
from devkit.files.search_log import search_file
from devkit.files.extract_code import extract_code_files
from devkit.files.batch_rename import batch_rename
```

- [ ] **Step 8: Add files CLI commands to devkit/cli.py**

Add after the `files` group:

```python
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
```

- [ ] **Step 9: Run tests**

Run: `pytest tests/test_files.py -v`
Expected: All tests pass.

- [ ] **Step 10: Commit**

```bash
git add devkit/files/ tests/test_files.py devkit/cli.py
git commit -m "feat: add files module (dedup, search, extract-code, batch-rename)"
```

---

## Task 5: Data Module

**Files:**
- Create: `devkit/data/json_utils.py`, `devkit/data/csv_utils.py`, `devkit/data/excel2csv.py`
- Modify: `devkit/cli.py`
- Test: `tests/test_data.py`

- [ ] **Step 1: Write tests**

```python
# tests/test_data.py
"""Tests for data processing tools."""

import csv
import json
import os

from devkit.data.json_utils import flatten_json, unflatten_json, json_query, merge_jsonl
from devkit.data.csv_utils import merge_csvs, split_csv, csv_to_json, json_to_csv


# --- json_utils tests ---

def test_flatten_json():
    data = {"a": {"b": {"c": 1}}, "d": 2}
    result = flatten_json(data)
    assert result == {"a.b.c": 1, "d": 2}


def test_flatten_json_custom_separator():
    data = {"a": {"b": 1}}
    result = flatten_json(data, separator="/")
    assert result == {"a/b": 1}


def test_unflatten_json():
    data = {"a.b.c": 1, "a.b.d": 2, "e": 3}
    result = unflatten_json(data)
    assert result == {"a": {"b": {"c": 1, "d": 2}}, "e": 3}


def test_json_query():
    data = {"a": {"b": [1, 2, 3]}}
    assert json_query(data, "a.b") == [1, 2, 3]
    assert json_query(data, "a") == {"b": [1, 2, 3]}
    assert json_query(data, "x.y") is None


def test_merge_jsonl(tmp_path):
    f1 = tmp_path / "a.jsonl"
    f2 = tmp_path / "b.jsonl"
    f1.write_text('{"x": 1}\n{"x": 2}\n')
    f2.write_text('{"x": 3}\n')
    out = str(tmp_path / "merged.jsonl")
    merge_jsonl([str(f1), str(f2)], out)
    with open(out) as f:
        lines = f.readlines()
    assert len(lines) == 3


# --- csv_utils tests ---

def test_merge_csvs(tmp_path):
    for i, rows in enumerate([
        [["name", "age"], ["Alice", "30"]],
        [["name", "age"], ["Bob", "25"]],
    ]):
        f = tmp_path / f"f{i}.csv"
        with open(f, "w", newline="") as csvfile:
            csv.writer(csvfile).writerows(rows)

    out = str(tmp_path / "merged.csv")
    merge_csvs([str(tmp_path / "f0.csv"), str(tmp_path / "f1.csv")], out)

    with open(out) as f:
        reader = csv.reader(f)
        rows = list(reader)
    assert len(rows) == 3  # header + 2 data rows


def test_split_csv(tmp_path):
    f = tmp_path / "big.csv"
    with open(f, "w", newline="") as csvfile:
        w = csv.writer(csvfile)
        w.writerow(["id", "value"])
        for i in range(10):
            w.writerow([i, f"val_{i}"])

    out_dir = str(tmp_path / "splits")
    split_csv(str(f), rows_per_file=3, output_dir=out_dir)
    split_files = os.listdir(out_dir)
    assert len(split_files) == 4  # 10 rows / 3 = 4 files (last has 1)


def test_csv_to_json(tmp_path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("name,age\nAlice,30\nBob,25\n")
    out = str(tmp_path / "data.json")
    csv_to_json(str(csv_file), out)
    with open(out) as f:
        data = json.load(f)
    assert len(data) == 2
    assert data[0]["name"] == "Alice"


def test_json_to_csv(tmp_path):
    json_file = tmp_path / "data.json"
    json_file.write_text('[{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]')
    out = str(tmp_path / "data.csv")
    json_to_csv(str(json_file), out)
    with open(out) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) == 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_data.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement devkit/data/json_utils.py**

```python
"""JSON processing utilities."""

import json
import os
from typing import Any, Optional


def flatten_json(data: dict, separator: str = ".", prefix: str = "") -> dict:
    """Flatten a nested dict into a single-level dict with dotted keys.

    Args:
        data: Nested dictionary.
        separator: Key separator.
        prefix: Key prefix (used for recursion).

    Returns:
        Flattened dictionary.
    """
    result = {}
    for key, value in data.items():
        new_key = f"{prefix}{separator}{key}" if prefix else key
        if isinstance(value, dict):
            result.update(flatten_json(value, separator, new_key))
        else:
            result[new_key] = value
    return result


def unflatten_json(data: dict, separator: str = ".") -> dict:
    """Unflatten a dotted-key dict into a nested dict.

    Args:
        data: Flat dictionary with dotted keys.
        separator: Key separator.

    Returns:
        Nested dictionary.
    """
    result: dict = {}
    for compound_key, value in data.items():
        keys = compound_key.split(separator)
        current = result
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
    return result


def json_query(data: Any, path: str, separator: str = ".") -> Optional[Any]:
    """Query a nested dict using dot-notation path.

    Args:
        data: Data to query.
        path: Dot-separated path (e.g., "a.b.c").
        separator: Path separator.

    Returns:
        Value at path, or None if not found.
    """
    keys = path.split(separator)
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    return current


def merge_jsonl(files: list, output: str) -> None:
    """Merge multiple JSONL files into one.

    Args:
        files: List of input JSONL file paths.
        output: Output file path.
    """
    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    with open(output, "w", encoding="utf-8") as out:
        for filepath in files:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        out.write(line + "\n")
```

- [ ] **Step 4: Implement devkit/data/csv_utils.py**

```python
"""CSV processing utilities."""

import csv
import json
import os
from typing import List, Optional


def merge_csvs(files: List[str], output: str) -> None:
    """Merge multiple CSV files into one (assumes same headers).

    Args:
        files: List of input CSV file paths.
        output: Output file path.
    """
    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    header_written = False

    with open(output, "w", newline="", encoding="utf-8") as out:
        writer = None
        for filepath in files:
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)
                if not header_written:
                    writer = csv.writer(out)
                    writer.writerow(header)
                    header_written = True
                for row in reader:
                    writer.writerow(row)


def split_csv(file: str, rows_per_file: int, output_dir: str) -> List[str]:
    """Split a large CSV into smaller files.

    Args:
        file: Input CSV file path.
        rows_per_file: Maximum rows per output file.
        output_dir: Directory for output files.

    Returns:
        List of output file paths.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_files = []

    with open(file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)

        file_index = 1
        current_rows: list = []

        for row in reader:
            current_rows.append(row)
            if len(current_rows) >= rows_per_file:
                out_path = os.path.join(output_dir, f"part_{file_index:03d}.csv")
                _write_csv(out_path, header, current_rows)
                output_files.append(out_path)
                current_rows = []
                file_index += 1

        if current_rows:
            out_path = os.path.join(output_dir, f"part_{file_index:03d}.csv")
            _write_csv(out_path, header, current_rows)
            output_files.append(out_path)

    return output_files


def _write_csv(path: str, header: list, rows: list) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def csv_to_json(file: str, output: str) -> None:
    """Convert CSV to JSON array.

    Args:
        file: Input CSV file path.
        output: Output JSON file path.
    """
    with open(file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        data = list(reader)

    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def json_to_csv(file: str, output: str) -> None:
    """Convert JSON array to CSV.

    Args:
        file: Input JSON file path (must contain a list of objects).
        output: Output CSV file path.
    """
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        return

    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    fieldnames = list(data[0].keys())
    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
```

- [ ] **Step 5: Implement devkit/data/excel2csv.py**

```python
"""Excel to CSV converter."""

import csv
import os
from typing import List, Optional


def list_sheets(file: str) -> List[str]:
    """List sheet names in an Excel file.

    Args:
        file: Path to Excel file.

    Returns:
        List of sheet names.
    """
    try:
        from openpyxl import load_workbook
    except ImportError:
        raise ImportError("openpyxl is required: pip install devkit-tools[data]")

    wb = load_workbook(file, read_only=True)
    names = wb.sheetnames
    wb.close()
    return names


def excel_to_csv(file: str, output: str, sheet: Optional[str] = None) -> None:
    """Convert an Excel sheet to CSV.

    Args:
        file: Path to Excel file.
        output: Output CSV file path.
        sheet: Sheet name (defaults to first sheet).
    """
    try:
        from openpyxl import load_workbook
    except ImportError:
        raise ImportError("openpyxl is required: pip install devkit-tools[data]")

    wb = load_workbook(file, read_only=True)
    ws = wb[sheet] if sheet else wb.active

    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for row in ws.iter_rows(values_only=True):
            writer.writerow(row)

    wb.close()
```

- [ ] **Step 6: Update devkit/data/__init__.py**

```python
"""Data processing tools."""

from devkit.data.json_utils import flatten_json, unflatten_json, json_query, merge_jsonl
from devkit.data.csv_utils import merge_csvs, split_csv, csv_to_json, json_to_csv
```

- [ ] **Step 7: Add data CLI commands to devkit/cli.py**

```python
# --- Data commands ---

@data.command("json-flatten")
@click.argument("input_file")
@click.option("-o", "--output", default=None, help="Output file")
def data_json_flatten(input_file, output):
    """Flatten nested JSON to dot-notation keys."""
    from devkit.data.json_utils import flatten_json

    with open(input_file, "r", encoding="utf-8") as f:
        original = json.load(f)
    result = flatten_json(original)
    out = json.dumps(result, indent=2, ensure_ascii=False)
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
```

Add `import json` to the top of `cli.py` imports if not already present.

- [ ] **Step 8: Run tests**

Run: `pytest tests/test_data.py -v`
Expected: All tests pass.

- [ ] **Step 9: Commit**

```bash
git add devkit/data/ tests/test_data.py devkit/cli.py
git commit -m "feat: add data module (JSON flatten/merge/query, CSV merge/split/convert, Excel2CSV)"
```

---

## Task 6: AI Module

**Files:**
- Create: `devkit/ai/token_counter.py`, `devkit/ai/prompt_template.py`, `devkit/ai/cost_calculator.py`
- Modify: `devkit/cli.py`
- Test: `tests/test_ai.py`

- [ ] **Step 1: Write tests**

```python
# tests/test_ai.py
"""Tests for AI/LLM utility tools."""

import os
import tempfile

from devkit.ai.cost_calculator import calculate_cost, compare_costs, supported_models
from devkit.ai.prompt_template import render_template, save_template, load_template, list_templates


# --- cost_calculator tests ---

def test_calculate_cost_gpt4o():
    cost = calculate_cost("gpt-4o", input_tokens=1000, output_tokens=500)
    assert isinstance(cost, float)
    assert cost > 0


def test_calculate_cost_unknown_model():
    cost = calculate_cost("unknown-model", input_tokens=1000, output_tokens=500)
    assert cost is None


def test_compare_costs():
    result = compare_costs(input_tokens=1000, output_tokens=500)
    assert isinstance(result, dict)
    assert len(result) > 0
    for model, cost in result.items():
        assert isinstance(cost, float)


def test_supported_models():
    models = supported_models()
    assert "gpt-4o" in models
    assert "claude-sonnet" in models


# --- prompt_template tests ---

def test_render_template():
    template = "Hello, {name}! You are {age} years old."
    result = render_template(template, {"name": "Alice", "age": "30"})
    assert result == "Hello, Alice! You are 30 years old."


def test_render_template_jinja2():
    template = "Items: {% for item in items %}{{ item }}, {% endfor %}"
    result = render_template(template, {"items": ["a", "b", "c"]})
    assert "a" in result
    assert "b" in result


def test_save_and_load_template(tmp_path, monkeypatch):
    monkeypatch.setenv("DEVKIT_PROMPTS_DIR", str(tmp_path))
    save_template("test_prompt", "Hello {name}", prompts_dir=str(tmp_path))
    loaded = load_template("test_prompt", prompts_dir=str(tmp_path))
    assert loaded == "Hello {name}"


def test_list_templates(tmp_path):
    (tmp_path / "prompt_a.txt").write_text("template a")
    (tmp_path / "prompt_b.txt").write_text("template b")
    templates = list_templates(prompts_dir=str(tmp_path))
    assert "prompt_a" in templates
    assert "prompt_b" in templates
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_ai.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement devkit/ai/cost_calculator.py**

```python
"""LLM API cost estimator."""

from typing import Dict, List, Optional

# Pricing per 1M tokens (input, output) in USD
PRICING = {
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4-turbo": (10.00, 30.00),
    "gpt-4": (30.00, 60.00),
    "gpt-3.5-turbo": (0.50, 1.50),
    "claude-opus": (15.00, 75.00),
    "claude-sonnet": (3.00, 15.00),
    "claude-haiku": (0.25, 1.25),
    "gemini-pro": (1.25, 5.00),
    "gemini-flash": (0.075, 0.30),
}


def supported_models() -> List[str]:
    """Return list of supported model names."""
    return list(PRICING.keys())


def calculate_cost(
    model: str, input_tokens: int, output_tokens: int
) -> Optional[float]:
    """Calculate API cost for a given model and token count.

    Args:
        model: Model name (e.g., 'gpt-4o', 'claude-sonnet').
        input_tokens: Number of input tokens.
        output_tokens: Number of output tokens.

    Returns:
        Total cost in USD, or None if model is unknown.
    """
    if model not in PRICING:
        return None

    input_price, output_price = PRICING[model]
    cost = (input_tokens / 1_000_000) * input_price + (output_tokens / 1_000_000) * output_price
    return round(cost, 6)


def compare_costs(input_tokens: int, output_tokens: int) -> Dict[str, float]:
    """Compare costs across all supported models.

    Args:
        input_tokens: Number of input tokens.
        output_tokens: Number of output tokens.

    Returns:
        Dict mapping model name to cost in USD, sorted by cost.
    """
    costs = {}
    for model in PRICING:
        cost = calculate_cost(model, input_tokens, output_tokens)
        if cost is not None:
            costs[model] = cost
    return dict(sorted(costs.items(), key=lambda x: x[1]))
```

- [ ] **Step 4: Implement devkit/ai/prompt_template.py**

```python
"""Prompt template manager with Jinja2 support."""

import os
from typing import Dict, List, Optional

DEFAULT_PROMPTS_DIR = os.path.expanduser("~/.devkit/prompts")


def render_template(template: str, variables: Dict[str, str]) -> str:
    """Render a prompt template with variables.

    Supports both Python str.format() and Jinja2 syntax.

    Args:
        template: Template string.
        variables: Variable substitutions.

    Returns:
        Rendered string.
    """
    # Try Jinja2 first if template contains Jinja2 syntax
    if "{%" in template or "{{" in template:
        try:
            from jinja2 import Template
            j2 = Template(template)
            return j2.render(**variables)
        except ImportError:
            pass

    # Fall back to str.format
    return template.format(**variables)


def save_template(
    name: str, content: str, prompts_dir: Optional[str] = None
) -> str:
    """Save a prompt template to disk.

    Args:
        name: Template name.
        content: Template content.
        prompts_dir: Directory to save to.

    Returns:
        Path to saved file.
    """
    directory = prompts_dir or DEFAULT_PROMPTS_DIR
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, f"{name}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def load_template(name: str, prompts_dir: Optional[str] = None) -> Optional[str]:
    """Load a prompt template from disk.

    Args:
        name: Template name.
        prompts_dir: Directory to load from.

    Returns:
        Template content, or None if not found.
    """
    directory = prompts_dir or DEFAULT_PROMPTS_DIR
    path = os.path.join(directory, f"{name}.txt")
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def list_templates(prompts_dir: Optional[str] = None) -> List[str]:
    """List available prompt templates.

    Args:
        prompts_dir: Directory to list from.

    Returns:
        List of template names.
    """
    directory = prompts_dir or DEFAULT_PROMPTS_DIR
    if not os.path.isdir(directory):
        return []
    return [f.rsplit(".", 1)[0] for f in os.listdir(directory) if f.endswith(".txt")]
```

- [ ] **Step 5: Implement devkit/ai/token_counter.py**

```python
"""Token counter for LLM models."""

from typing import List, Optional


MODEL_ENCODINGS = {
    "gpt-4o": "o200k_base",
    "gpt-4o-mini": "o200k_base",
    "gpt-4-turbo": "cl100k_base",
    "gpt-4": "cl100k_base",
    "gpt-3.5-turbo": "cl100k_base",
    "claude-opus": "cl100k_base",
    "claude-sonnet": "cl100k_base",
    "claude-haiku": "cl100k_base",
}


def supported_models() -> List[str]:
    """Return list of supported models for token counting."""
    return list(MODEL_ENCODINGS.keys())


def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """Count tokens in text for a given model.

    Args:
        text: Input text.
        model: Model name.

    Returns:
        Token count.

    Raises:
        ImportError: If tiktoken is not installed.
    """
    try:
        import tiktoken
    except ImportError:
        raise ImportError("tiktoken is required: pip install devkit-tools[ai]")

    encoding_name = MODEL_ENCODINGS.get(model, "cl100k_base")
    enc = tiktoken.get_encoding(encoding_name)
    return len(enc.encode(text))


def count_tokens_file(file_path: str, model: str = "gpt-4o") -> int:
    """Count tokens in a file.

    Args:
        file_path: Path to text file.
        model: Model name.

    Returns:
        Token count.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    return count_tokens(text, model)
```

- [ ] **Step 6: Update devkit/ai/__init__.py**

```python
"""AI/LLM utility tools."""

from devkit.ai.cost_calculator import calculate_cost, compare_costs
from devkit.ai.prompt_template import render_template, save_template, load_template, list_templates
```

- [ ] **Step 7: Add AI CLI commands to devkit/cli.py**

```python
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
        vars_dict = json.loads(variables)
        click.echo(render_template(template, vars_dict))
    else:
        click.echo(template)
```

- [ ] **Step 8: Run tests**

Run: `pytest tests/test_ai.py -v`
Expected: All tests pass (token_counter tests skipped if tiktoken not installed).

- [ ] **Step 9: Commit**

```bash
git add devkit/ai/ tests/test_ai.py devkit/cli.py
git commit -m "feat: add AI module (token counter, prompt templates, cost calculator)"
```

---

## Task 7: Text Module (Migrate + New)

**Files:**
- Create: `devkit/text/text_length.py`, `devkit/text/keywords.py`, `devkit/text/split_sentence.py`, `devkit/text/tokenizer.py`
- Modify: `devkit/cli.py`
- Test: `tests/test_text.py`

Migrates from `good_codes/calculate_text_length.py`, `good_codes/weighted_keywords.py`, `tools/python-tools/split_sents.py`. Cleans up code: removes sys.path hacks, adds type hints, removes prints.

- [ ] **Step 1: Write tests**

```python
# tests/test_text.py
"""Tests for text processing tools."""

from devkit.text.text_length import calculate_custom_length
from devkit.text.split_sentence import split_sentence


# --- text_length tests ---

def test_text_length_english():
    result = calculate_custom_length("Hello world")
    assert isinstance(result, int)
    assert result >= 0


def test_text_length_chinese():
    result = calculate_custom_length("你好世界")
    assert result == 4


def test_text_length_mixed():
    result = calculate_custom_length("Hello 你好 World")
    assert result > 0


def test_text_length_empty():
    result = calculate_custom_length("")
    assert result == 0


# --- split_sentence tests ---

def test_split_sentence_coarse():
    text = "第一句话。第二句话。第三句话。"
    result = split_sentence(text, criterion="coarse")
    assert len(result) == 3


def test_split_sentence_fine():
    text = "你好，世界！今天天气很好。"
    result = split_sentence(text, criterion="fine")
    assert len(result) >= 2


def test_split_sentence_empty():
    result = split_sentence("", criterion="coarse")
    assert result == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_text.py -v`
Expected: FAIL

- [ ] **Step 3: Implement devkit/text/text_length.py**

Migrate from `good_codes/calculate_text_length.py` — cleaned up version:

```python
"""Information-entropy based text length calculation.

Assigns weights to different character types based on their information density:
- CJK characters: 1.0 (high density)
- English words: 0.47 per word (semantic unit)
- Numbers: 0.01 per digit
- Spaces: 0.001
- Punctuation: 0.05
- Emoji: 0.2
"""

import math
import re
import unicodedata

_PATTERN = re.compile(
    r"(?P<word>\b[a-zA-Z]+\b)"
    r"|(?P<mixed>[a-zA-Z0-9]*[a-zA-Z][a-zA-Z0-9]*[0-9][a-zA-Z0-9]*|[a-zA-Z0-9]*[0-9][a-zA-Z0-9]*[a-zA-Z][a-zA-Z0-9]*)"
    r"|(?P<digit>\b\d+\b)"
    r"|(?P<space>\s+)"
    r"|(?P<punctuation>[\u2000-\u206F\u2E00-\u2E7F'!\"#$%&()*+,\-./:;<=>?@\[\]^_`{|}~])"
    r"|(?P<fullwidth>[\uFF00-\uFFEF])"
    r"|(?P<control>[\u0000-\u001F\u007F-\u009F])"
    r"|(?P<emoji>[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF])",
    re.UNICODE,
)


def _unclassified_length(text: str) -> float:
    """Calculate length for characters not matched by the main pattern."""
    length = 0.0
    for char in text:
        if "\u4E00" <= char <= "\u9FFF" or "\u3400" <= char <= "\u4DBF":
            length += 1.0
        elif "\uFF65" <= char <= "\uFF9F":
            length += 0.7
        else:
            cat = unicodedata.category(char)
            if cat.startswith("L"):
                length += 0.5
            elif cat.startswith("M"):
                length += 0.3
            elif cat.startswith("N"):
                length += 0.01
            elif cat.startswith("S"):
                length += 0.2
            else:
                length += 0.3
    return length


def calculate_custom_length(text: str) -> int:
    """Calculate information-weighted text length.

    Args:
        text: Input text string.

    Returns:
        Weighted length as integer (floor).
    """
    if not text:
        return 0

    total = 0.0
    last_index = 0

    for match in _PATTERN.finditer(text):
        start, end = match.span()
        if last_index < start:
            total += _unclassified_length(text[last_index:start])
        last_index = end

        if match.group("word"):
            total += 0.47
        elif match.group("mixed"):
            total += len(match.group("mixed")) * 0.01
        elif match.group("digit"):
            total += len(match.group("digit")) * 0.01
        elif match.group("space"):
            total += len(match.group("space")) * 0.001
        elif match.group("punctuation"):
            total += 0.05
        elif match.group("fullwidth"):
            total += 0.8
        elif match.group("control"):
            continue
        elif match.group("emoji"):
            total += 0.2

    if last_index < len(text):
        total += _unclassified_length(text[last_index:])

    return math.floor(total)
```

- [ ] **Step 4: Implement devkit/text/split_sentence.py**

Migrate from `tools/python-tools/split_sents.py` — cleaned up, standalone (no jionlp dependency):

```python
"""Chinese sentence splitter.

Splits Chinese text into sentences with proper handling of quotation marks.
Supports coarse (period-level) and fine (all punctuation) granularity.
"""

import re
from typing import List


_PUNCS_FINE = {"……", "\r\n", "，", "。", ";", "；", "…", "！", "!",
               "?", "？", "\r", "\n", "\u201c", "\u201d", "\u2018", "\u2019", "："}
_PUNCS_COARSE = {"。", "！", "？", "\n", "\u201c", "\u201d", "\u2018", "\u2019"}
_FRONT_QUOTES = {"\u201c", "\u2018"}
_BACK_QUOTES = {"\u201d", "\u2019"}

_COARSE_PTN = re.compile('([。\u201c\u201d！？\n])')
_FINE_PTN = re.compile('([，：。;\u201c\u201d；…！!?？\r\n])')


def split_sentence(text: str, criterion: str = "coarse") -> List[str]:
    """Split text into sentences.

    Args:
        text: Input text.
        criterion: 'coarse' (sentence-level) or 'fine' (clause-level).

    Returns:
        List of sentence strings.
    """
    if not text or not text.strip():
        return []

    if criterion == "coarse":
        tmp_list = _COARSE_PTN.split(text)
        puncs = _PUNCS_COARSE
    elif criterion == "fine":
        tmp_list = _FINE_PTN.split(text)
        puncs = _PUNCS_FINE
    else:
        raise ValueError("criterion must be 'coarse' or 'fine'")

    sentences: List[str] = []
    quote_flag = False

    for seg in tmp_list:
        if seg == "":
            continue

        if seg in puncs:
            if len(sentences) == 0:
                if seg in _FRONT_QUOTES:
                    quote_flag = True
                sentences.append(seg)
                continue

            if seg in _FRONT_QUOTES:
                if sentences[-1][-1] in puncs:
                    sentences.append(seg)
                else:
                    sentences[-1] += seg
                quote_flag = True
            else:
                sentences[-1] += seg
            continue

        if len(sentences) == 0:
            sentences.append(seg)
            continue

        if quote_flag:
            sentences[-1] += seg
            quote_flag = False
        else:
            if sentences[-1][-1] in _BACK_QUOTES:
                if len(sentences[-1]) <= 1:
                    sentences[-1] += seg
                else:
                    if sentences[-1][-2] in puncs:
                        sentences.append(seg)
                    else:
                        sentences[-1] += seg
            else:
                sentences.append(seg)

    return sentences
```

- [ ] **Step 5: Create stub devkit/text/keywords.py and devkit/text/tokenizer.py**

`devkit/text/keywords.py` — simplified migration (full WeightedKeywordExtractor requires jieba):

```python
"""Weighted keyword extraction for Chinese and English text.

Requires: jieba (pip install devkit-tools[nlp])
"""

from typing import Dict, List, Optional, Union


def extract_keywords(
    text: str, lang: str = "zh", mode: str = "all", top_k: int = 10
) -> List[Dict[str, Union[str, float]]]:
    """Extract weighted keywords from text.

    Args:
        text: Input text.
        lang: Language ('zh' for Chinese, 'en' for English).
        mode: 'all' to keep all, 'filter' to remove overlapping keywords.
        top_k: Maximum keywords to return.

    Returns:
        List of dicts with 'word' and 'boost' keys.
    """
    text = str(text).strip()
    if not text:
        return []

    if lang == "en":
        return _extract_english(text, top_k)
    return _extract_chinese(text, mode, top_k)


def _extract_english(text: str, top_k: int) -> List[Dict[str, Union[str, float]]]:
    """Simple English keyword extraction using word frequency."""
    import re
    words = re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())
    stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
                  "being", "have", "has", "had", "do", "does", "did", "will",
                  "would", "could", "should", "may", "might", "can", "shall",
                  "of", "in", "to", "for", "with", "on", "at", "from", "by",
                  "as", "into", "through", "during", "before", "after", "and",
                  "but", "or", "nor", "not", "so", "yet", "both", "either",
                  "neither", "each", "every", "all", "any", "few", "more",
                  "most", "other", "some", "such", "no", "only", "own", "same",
                  "than", "too", "very", "just", "because", "this", "that",
                  "these", "those", "it", "its"}
    words = [w for w in words if w not in stop_words]

    freq: Dict[str, int] = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1

    sorted_words = sorted(freq.items(), key=lambda x: -x[1])
    max_freq = sorted_words[0][1] if sorted_words else 1
    return [
        {"word": w, "boost": round(c / max_freq * 2, 2)}
        for w, c in sorted_words[:top_k]
    ]


def _extract_chinese(
    text: str, mode: str, top_k: int
) -> List[Dict[str, Union[str, float]]]:
    """Chinese keyword extraction using jieba TF-IDF."""
    try:
        import jieba.analyse as analyse
    except ImportError:
        raise ImportError("jieba is required: pip install devkit-tools[nlp]")

    allow_pos = ("n", "ns", "nt", "nz", "v", "vn", "a", "an", "eng")
    extracted = analyse.extract_tags(text, topK=top_k, withWeight=True, allowPOS=allow_pos)

    if not extracted:
        return [{"word": text, "boost": 2.0}]

    max_weight = extracted[0][1] if extracted else 1
    return [
        {"word": word, "boost": round(weight / max_weight * 2, 2)}
        for word, weight in extracted
    ]
```

`devkit/text/tokenizer.py`:

```python
"""Simple tokenizer utilities (word/char level, no external deps)."""

import re
from typing import List


def word_tokenize(text: str) -> List[str]:
    """Simple word tokenizer for mixed CJK/English text.

    Args:
        text: Input text.

    Returns:
        List of tokens.
    """
    tokens = []
    # Split CJK characters individually, keep English words together
    for segment in re.findall(r"[\u4e00-\u9fff]|[a-zA-Z]+|[0-9]+", text):
        tokens.append(segment)
    return tokens


def char_count(text: str) -> dict:
    """Count characters by category.

    Args:
        text: Input text.

    Returns:
        Dict with counts for 'cjk', 'english', 'digits', 'spaces', 'other'.
    """
    counts = {"cjk": 0, "english": 0, "digits": 0, "spaces": 0, "punctuation": 0, "other": 0}
    for char in text:
        if "\u4E00" <= char <= "\u9FFF":
            counts["cjk"] += 1
        elif char.isalpha():
            counts["english"] += 1
        elif char.isdigit():
            counts["digits"] += 1
        elif char.isspace():
            counts["spaces"] += 1
        elif not char.isalnum():
            counts["punctuation"] += 1
        else:
            counts["other"] += 1
    return counts
```

- [ ] **Step 6: Update devkit/text/__init__.py**

```python
"""Text & NLP processing tools."""

from devkit.text.text_length import calculate_custom_length
from devkit.text.split_sentence import split_sentence
from devkit.text.tokenizer import word_tokenize, char_count
```

- [ ] **Step 7: Add text CLI commands to devkit/cli.py**

```python
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
```

- [ ] **Step 8: Run tests**

Run: `pytest tests/test_text.py -v`
Expected: All tests pass.

- [ ] **Step 9: Commit**

```bash
git add devkit/text/ tests/test_text.py devkit/cli.py
git commit -m "feat: add text module (text length, keywords, sentence splitter, tokenizer)"
```

---

## Task 8: Web Module

**Files:**
- Create: `devkit/web/qr_code.py`, `devkit/web/url_validator.py`
- Modify: `devkit/cli.py`
- Test: `tests/test_web.py`

- [ ] **Step 1: Write tests**

```python
# tests/test_web.py
"""Tests for web utility tools."""

from devkit.web.url_validator import is_valid_url


def test_valid_urls():
    assert is_valid_url("https://example.com") is True
    assert is_valid_url("http://example.com/path") is True
    assert is_valid_url("https://sub.example.com:8080/path?q=1") is True


def test_invalid_urls():
    assert is_valid_url("not a url") is False
    assert is_valid_url("") is False
    assert is_valid_url("ftp://files.example.com") is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_web.py -v`
Expected: FAIL

- [ ] **Step 3: Implement devkit/web/url_validator.py**

```python
"""URL validation and metadata extraction."""

from typing import Dict, Optional
from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    """Check if a URL is valid (http/https only).

    Args:
        url: URL string to validate.

    Returns:
        True if valid.
    """
    if not url:
        return False
    try:
        result = urlparse(url)
        return result.scheme in ("http", "https") and bool(result.netloc)
    except ValueError:
        return False


def get_metadata(url: str) -> Optional[Dict[str, str]]:
    """Fetch URL and extract metadata (title, description).

    Args:
        url: URL to fetch.

    Returns:
        Dict with 'title', 'description', 'status_code', or None on failure.

    Requires: requests, beautifulsoup4 (pip install devkit-tools[web])
    """
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        raise ImportError("requests and beautifulsoup4 required: pip install devkit-tools[web]")

    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "devkit/0.1"})
        soup = BeautifulSoup(resp.text, "html.parser")

        title_tag = soup.find("title")
        title = title_tag.string.strip() if title_tag and title_tag.string else ""

        desc_tag = soup.find("meta", attrs={"name": "description"})
        description = desc_tag.get("content", "").strip() if desc_tag else ""

        return {
            "url": url,
            "status_code": str(resp.status_code),
            "title": title,
            "description": description,
        }
    except Exception as e:
        return {"url": url, "error": str(e)}
```

- [ ] **Step 4: Implement devkit/web/qr_code.py**

```python
"""QR code generation and reading."""

import os
from typing import Optional


def generate_qr(data: str, output: str, size: int = 300) -> str:
    """Generate a QR code image.

    Args:
        data: Text or URL to encode.
        output: Output image path.
        size: Image size in pixels.

    Returns:
        Path to generated image.

    Requires: qrcode, Pillow (pip install devkit-tools[web])
    """
    try:
        import qrcode
    except ImportError:
        raise ImportError("qrcode is required: pip install devkit-tools[web]")

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((size, size))

    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    img.save(output)
    return output


def read_qr(image_path: str) -> Optional[str]:
    """Read QR code from an image.

    Args:
        image_path: Path to image containing QR code.

    Returns:
        Decoded string, or None if no QR code found.

    Requires: pyzbar, Pillow (pip install devkit-tools[web])
    """
    try:
        from PIL import Image
        from pyzbar.pyzbar import decode
    except ImportError:
        raise ImportError("pyzbar and Pillow required: pip install devkit-tools[web]")

    img = Image.open(image_path)
    decoded = decode(img)
    if decoded:
        return decoded[0].data.decode("utf-8")
    return None
```

- [ ] **Step 5: Update devkit/web/__init__.py**

```python
"""Web utility tools."""

from devkit.web.url_validator import is_valid_url
```

- [ ] **Step 6: Add web CLI commands to devkit/cli.py**

```python
# --- Web commands ---

@web.command("qrcode")
@click.argument("data")
@click.option("-o", "--output", default="qr.png", help="Output image path")
@click.option("--size", default=300, help="Image size in pixels")
def web_qrcode(data, output, size):
    """Generate a QR code image."""
    from devkit.web.qr_code import generate_qr

    path = generate_qr(data, output, size=size)
    click.echo(f"QR code saved to {path}")


@web.command("qrcode-read")
@click.argument("image")
def web_qrcode_read(image):
    """Read QR code from an image."""
    from devkit.web.qr_code import read_qr

    result = read_qr(image)
    if result:
        click.echo(result)
    else:
        click.echo("No QR code found in image.", err=True)


@web.command("validate-url")
@click.argument("url")
@click.option("--metadata", is_flag=True, help="Fetch and show page metadata")
def web_validate_url(url, metadata):
    """Validate a URL."""
    from devkit.web.url_validator import is_valid_url, get_metadata

    if not is_valid_url(url):
        click.echo(f"Invalid URL: {url}", err=True)
        raise SystemExit(1)

    click.echo(f"Valid URL: {url}")
    if metadata:
        meta = get_metadata(url)
        if meta:
            for k, v in meta.items():
                click.echo(f"  {k}: {v}")
```

- [ ] **Step 7: Run tests**

Run: `pytest tests/test_web.py -v`
Expected: All tests pass.

- [ ] **Step 8: Commit**

```bash
git add devkit/web/ tests/test_web.py devkit/cli.py
git commit -m "feat: add web module (QR code, URL validator)"
```

---

## Task 9: Convert Module (Migrate Existing)

**Files:**
- Create: `devkit/convert/pdf_merge.py`, `devkit/convert/pdf_compress.py`, `devkit/convert/media.py`, `devkit/convert/md2pdf.py`, `devkit/convert/md2docx.py`, `devkit/convert/pdf_parse.py`, `devkit/convert/doc_convert.py`
- Modify: `devkit/cli.py`
- Test: `tests/test_convert.py`

These tools wrap external dependencies (PyMuPDF, ffmpeg, Ghostscript, Pillow). Tests will be minimal since most require system tools.

- [ ] **Step 1: Write tests**

```python
# tests/test_convert.py
"""Tests for conversion tools."""

import os

from devkit.convert.pdf_merge import merge_pdfs
from devkit.convert.media import webp_to_png, resize_image


def test_merge_pdfs_empty_dir(tmp_path):
    out = str(tmp_path / "out.pdf")
    count = merge_pdfs(str(tmp_path), out)
    assert count == 0


def test_resize_image_missing_file():
    result = resize_image("/nonexistent.jpg", "300x300")
    assert result is None
```

- [ ] **Step 2: Implement devkit/convert/pdf_merge.py**

```python
"""Merge multiple PDF files."""

import os
from typing import Optional


def merge_pdfs(input_dir: str, output_file: str) -> int:
    """Merge all PDF files in a directory into a single PDF.

    Args:
        input_dir: Directory containing PDF files.
        output_file: Output merged PDF path.

    Returns:
        Number of PDFs merged.

    Requires: PyPDF2 (pip install devkit-tools[convert])
    """
    try:
        from PyPDF2 import PdfMerger
    except ImportError:
        raise ImportError("PyPDF2 is required: pip install devkit-tools[convert]")

    pdf_files = sorted(f for f in os.listdir(input_dir) if f.lower().endswith(".pdf"))
    if not pdf_files:
        return 0

    merger = PdfMerger()
    for pdf_file in pdf_files:
        merger.append(os.path.join(input_dir, pdf_file))

    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
    with open(output_file, "wb") as f:
        merger.write(f)
    merger.close()

    return len(pdf_files)
```

- [ ] **Step 3: Implement devkit/convert/pdf_compress.py**

```python
"""Compress PDF files using Ghostscript."""

import os
import shutil
import subprocess
from typing import Optional


QUALITY_SETTINGS = {
    "screen": "/screen",
    "ebook": "/ebook",
    "printer": "/printer",
    "prepress": "/prepress",
}


def compress_pdf(
    input_path: str, output_path: Optional[str] = None, quality: str = "ebook"
) -> Optional[str]:
    """Compress a PDF file using Ghostscript.

    Args:
        input_path: Input PDF file path.
        output_path: Output path (defaults to input with _compressed suffix).
        quality: Quality setting (screen, ebook, printer, prepress).

    Returns:
        Output file path, or None if Ghostscript is not available.
    """
    if not shutil.which("gs"):
        raise FileNotFoundError("Ghostscript (gs) is required but not found. Install it first.")

    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_compressed{ext}"

    setting = QUALITY_SETTINGS.get(quality, "/ebook")

    result = subprocess.run(
        [
            "gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS={setting}", "-dNOPAUSE", "-dQUIET", "-dBATCH",
            f"-sOutputFile={output_path}", input_path,
        ],
        capture_output=True,
    )

    if result.returncode == 0:
        return output_path
    return None
```

- [ ] **Step 4: Implement devkit/convert/media.py**

```python
"""Media conversion tools (video, image)."""

import os
import shutil
import subprocess
from typing import Optional


def mp4_to_mp3(input_path: str, output_path: Optional[str] = None) -> Optional[str]:
    """Convert MP4 to MP3 using ffmpeg.

    Args:
        input_path: Input MP4 file path.
        output_path: Output MP3 path.

    Returns:
        Output file path, or None on failure.
    """
    if not shutil.which("ffmpeg"):
        raise FileNotFoundError("ffmpeg is required but not found.")

    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + ".mp3"

    result = subprocess.run(
        ["ffmpeg", "-i", input_path, "-vn", "-acodec", "libmp3lame",
         "-q:a", "2", output_path, "-y"],
        capture_output=True,
    )
    return output_path if result.returncode == 0 else None


def webp_to_png(input_path: str, output_path: Optional[str] = None) -> Optional[str]:
    """Convert WebP to PNG using Pillow.

    Args:
        input_path: Input WebP file path.
        output_path: Output PNG path.

    Returns:
        Output file path, or None on failure.
    """
    try:
        from PIL import Image
    except ImportError:
        raise ImportError("Pillow is required: pip install devkit-tools[convert]")

    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + ".png"

    try:
        img = Image.open(input_path)
        img.save(output_path, "PNG")
        return output_path
    except Exception:
        return None


def resize_image(
    input_path: str, size: str, output_path: Optional[str] = None
) -> Optional[str]:
    """Resize an image.

    Args:
        input_path: Input image path.
        size: Size string (e.g., '300' for square, '800x600' for rectangle).
        output_path: Output path.

    Returns:
        Output file path, or None on failure.
    """
    try:
        from PIL import Image
    except ImportError:
        raise ImportError("Pillow is required: pip install devkit-tools[convert]")

    if not os.path.isfile(input_path):
        return None

    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_resized{ext}"

    if "x" in size:
        width, height = map(int, size.split("x"))
    else:
        width = height = int(size)

    try:
        img = Image.open(input_path)
        img = img.resize((width, height))
        img.save(output_path)
        return output_path
    except Exception:
        return None
```

- [ ] **Step 5: Create stub files for md2pdf.py, md2docx.py, pdf_parse.py, doc_convert.py**

`devkit/convert/md2pdf.py`:
```python
"""Markdown to PDF converter."""

import os
from typing import Optional


def markdown_to_pdf(input_path: str, output_path: Optional[str] = None) -> str:
    """Convert a Markdown file to PDF.

    Args:
        input_path: Input Markdown file path.
        output_path: Output PDF path.

    Returns:
        Output file path.

    Requires: markdown2, reportlab (pip install devkit-tools[convert])
    """
    try:
        import markdown2
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    except ImportError:
        raise ImportError("markdown2 and reportlab required: pip install devkit-tools[convert]")

    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + ".pdf"

    with open(input_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    html_content = markdown2.markdown(md_content)
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()

    content = []
    import re
    for para in re.split(r"\n\s*\n", html_content):
        clean = re.sub(r"<[^>]+>", "", para).strip()
        if clean:
            content.append(Paragraph(clean, styles["Normal"]))
            content.append(Spacer(1, 12))

    if content:
        doc.build(content)

    return output_path
```

`devkit/convert/md2docx.py`:
```python
"""Markdown to DOCX converter."""

import os
from typing import Optional


def markdown_to_docx(input_path: str, output_path: Optional[str] = None) -> str:
    """Convert a Markdown file to DOCX.

    Args:
        input_path: Input Markdown file path.
        output_path: Output DOCX path.

    Returns:
        Output file path.

    Requires: markdown, python-docx, beautifulsoup4 (pip install devkit-tools[convert])
    """
    try:
        import markdown
        from bs4 import BeautifulSoup
        from docx import Document
    except ImportError:
        raise ImportError("markdown, python-docx, beautifulsoup4 required: pip install devkit-tools[convert]")

    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + ".docx"

    with open(input_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    html = markdown.markdown(md_text, extensions=["fenced_code", "tables"])
    soup = BeautifulSoup(html, "html.parser")
    doc = Document()

    for elem in soup.children:
        if not hasattr(elem, "name") or elem.name is None:
            continue
        text = elem.get_text()
        if elem.name == "h1":
            doc.add_heading(text, level=1)
        elif elem.name == "h2":
            doc.add_heading(text, level=2)
        elif elem.name == "h3":
            doc.add_heading(text, level=3)
        elif elem.name in ("p", "div"):
            doc.add_paragraph(text)
        elif elem.name in ("ul", "ol"):
            for li in elem.find_all("li", recursive=False):
                doc.add_paragraph(li.get_text(), style="List Bullet")
        elif elem.name == "pre":
            doc.add_paragraph(text, style="Normal")

    doc.save(output_path)
    return output_path
```

`devkit/convert/pdf_parse.py`:
```python
"""AI-powered PDF to Markdown parser."""

import os
from typing import Optional


def pdf_to_markdown(
    input_path: str,
    output_dir: Optional[str] = None,
    model: str = "gpt-4o",
    api_key: Optional[str] = None,
) -> str:
    """Parse a PDF and convert to Markdown using AI vision.

    This is a wrapper around the PDF parsing pipeline that uses
    AI models to extract text from PDF page images.

    Args:
        input_path: Input PDF file path.
        output_dir: Output directory for images and markdown.
        model: AI model to use.
        api_key: API key for the AI service.

    Returns:
        Path to generated markdown file.

    Requires: PyMuPDF, shapely (pip install devkit-tools[convert])
    """
    raise NotImplementedError(
        "PDF parsing requires AI API access. "
        "See devkit.convert.pdf_parse for the full implementation."
    )
```

`devkit/convert/doc_convert.py`:
```python
"""Document format conversion (Word, PDF, JPG, Markdown).

Requires system tools: LibreOffice, Pandoc, ImageMagick.
"""

import os
import shutil
import subprocess
from typing import Optional


def convert_document(input_path: str, to_format: str, output_path: Optional[str] = None) -> Optional[str]:
    """Convert between document formats.

    Supported conversions: Word->PDF, Word->Markdown, Markdown->Word

    Args:
        input_path: Input file path.
        to_format: Target format (pdf, md, docx).
        output_path: Output path.

    Returns:
        Output file path, or None on failure.
    """
    if to_format == "pdf" and input_path.endswith((".docx", ".doc")):
        return _word_to_pdf(input_path, output_path)
    elif to_format == "md" and input_path.endswith((".docx", ".doc")):
        return _word_to_markdown(input_path, output_path)
    elif to_format == "docx" and input_path.endswith(".md"):
        return _markdown_to_word(input_path, output_path)
    else:
        return None


def _word_to_pdf(input_path: str, output_path: Optional[str] = None) -> Optional[str]:
    if not shutil.which("libreoffice"):
        raise FileNotFoundError("LibreOffice is required for Word->PDF conversion.")
    out_dir = os.path.dirname(output_path) if output_path else "."
    os.makedirs(out_dir, exist_ok=True)
    result = subprocess.run(
        ["libreoffice", "--headless", "--convert-to", "pdf", input_path, "--outdir", out_dir],
        capture_output=True,
    )
    if result.returncode == 0:
        expected = os.path.join(out_dir, os.path.splitext(os.path.basename(input_path))[0] + ".pdf")
        return expected if os.path.exists(expected) else None
    return None


def _word_to_markdown(input_path: str, output_path: Optional[str] = None) -> Optional[str]:
    if not shutil.which("pandoc"):
        raise FileNotFoundError("Pandoc is required for Word->Markdown conversion.")
    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + ".md"
    result = subprocess.run(["pandoc", input_path, "-o", output_path], capture_output=True)
    return output_path if result.returncode == 0 else None


def _markdown_to_word(input_path: str, output_path: Optional[str] = None) -> Optional[str]:
    if not shutil.which("pandoc"):
        raise FileNotFoundError("Pandoc is required for Markdown->Word conversion.")
    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + ".docx"
    result = subprocess.run(["pandoc", input_path, "-o", output_path], capture_output=True)
    return output_path if result.returncode == 0 else None
```

- [ ] **Step 6: Update devkit/convert/__init__.py**

```python
"""Document & media conversion tools."""

from devkit.convert.pdf_merge import merge_pdfs
```

- [ ] **Step 7: Add convert CLI commands to devkit/cli.py**

```python
# --- Convert commands ---

@convert.command("pdf-merge")
@click.argument("directory")
@click.option("-o", "--output", default="merged.pdf", help="Output PDF path")
def convert_pdf_merge(directory, output):
    """Merge PDF files in a directory."""
    from devkit.convert.pdf_merge import merge_pdfs

    count = merge_pdfs(directory, output)
    click.echo(f"Merged {count} PDFs into {output}")


@convert.command("pdf-compress")
@click.argument("input_file")
@click.option("-o", "--output", default=None, help="Output path")
@click.option("--quality", default="ebook", type=click.Choice(["screen", "ebook", "printer", "prepress"]))
def convert_pdf_compress(input_file, output, quality):
    """Compress a PDF file."""
    from devkit.convert.pdf_compress import compress_pdf

    result = compress_pdf(input_file, output, quality=quality)
    if result:
        click.echo(f"Compressed: {result}")
    else:
        click.echo("Compression failed.", err=True)


@convert.command("mp4-to-mp3")
@click.argument("input_path")
def convert_mp4_to_mp3(input_path):
    """Convert MP4 video to MP3 audio."""
    from devkit.convert.media import mp4_to_mp3

    result = mp4_to_mp3(input_path)
    if result:
        click.echo(f"Converted: {result}")
    else:
        click.echo("Conversion failed.", err=True)


@convert.command("webp-to-png")
@click.argument("input_path")
@click.option("-o", "--output", default=None, help="Output path")
def convert_webp_to_png(input_path, output):
    """Convert WebP image to PNG."""
    from devkit.convert.media import webp_to_png

    result = webp_to_png(input_path, output)
    if result:
        click.echo(f"Converted: {result}")
    else:
        click.echo("Conversion failed.", err=True)


@convert.command("resize")
@click.argument("input_path")
@click.argument("size")
@click.option("-o", "--output", default=None, help="Output path")
def convert_resize(input_path, size, output):
    """Resize an image (e.g., '300' for square, '800x600')."""
    from devkit.convert.media import resize_image

    result = resize_image(input_path, size, output)
    if result:
        click.echo(f"Resized: {result}")
    else:
        click.echo("Resize failed.", err=True)


@convert.command("md2pdf")
@click.argument("input_path")
@click.option("-o", "--output", default=None, help="Output PDF path")
def convert_md2pdf(input_path, output):
    """Convert Markdown to PDF."""
    from devkit.convert.md2pdf import markdown_to_pdf

    result = markdown_to_pdf(input_path, output)
    click.echo(f"Converted: {result}")


@convert.command("md2docx")
@click.argument("input_path")
@click.option("-o", "--output", default=None, help="Output DOCX path")
def convert_md2docx(input_path, output):
    """Convert Markdown to DOCX."""
    from devkit.convert.md2docx import markdown_to_docx

    result = markdown_to_docx(input_path, output)
    click.echo(f"Converted: {result}")


@convert.command("doc")
@click.argument("input_path")
@click.option("--to", "to_format", required=True, type=click.Choice(["pdf", "md", "docx"]))
@click.option("-o", "--output", default=None, help="Output path")
def convert_doc(input_path, to_format, output):
    """Convert between document formats (requires LibreOffice/Pandoc)."""
    from devkit.convert.doc_convert import convert_document

    result = convert_document(input_path, to_format, output)
    if result:
        click.echo(f"Converted: {result}")
    else:
        click.echo("Conversion failed or unsupported format.", err=True)
```

- [ ] **Step 8: Run tests**

Run: `pytest tests/test_convert.py -v`
Expected: All tests pass.

- [ ] **Step 9: Commit**

```bash
git add devkit/convert/ tests/test_convert.py devkit/cli.py
git commit -m "feat: add convert module (PDF merge/compress, media tools, md2pdf, md2docx, doc convert)"
```

---

## Task 10: Documentation (README, CONTRIBUTING, CHANGELOG)

**Files:**
- Create: `README.md` (replace), `README_CN.md`, `CONTRIBUTING.md`, `CHANGELOG.md`

- [ ] **Step 1: Write README.md**

This is the most critical file. Write the full bilingual README with:
- Hero section with badges
- Features table
- Quick Start
- Collapsible `<details>` sections for each of the 7 tool categories
- Each category shows a table of tools with name, description, example
- Installation section (pip, from source, optional deps)
- Contributing link
- License
- Chinese section at bottom

The README should be comprehensive (300+ lines) with real working examples for every tool.

- [ ] **Step 2: Write README_CN.md**

Full Chinese translation of the README.

- [ ] **Step 3: Write CONTRIBUTING.md**

Standard contribution guide: fork, branch, install dev deps, run tests, PR guidelines.

- [ ] **Step 4: Write CHANGELOG.md**

```markdown
# Changelog

## [0.1.0] - 2026-03-28

### Added
- Initial release with 27+ tools across 7 categories
- Click-based CLI with `devkit` entry point
- Document & media conversion tools (PDF merge/compress, md2pdf, md2docx, media)
- Text & NLP tools (text length, keywords, sentence splitter, tokenizer)
- File management tools (dedup, search, extract-code, batch-rename)
- AI/LLM utilities (token counter, prompt templates, cost calculator)
- Data processing tools (JSON flatten/merge/query, CSV merge/split, Excel2CSV)
- Web utilities (QR code, URL validator)
- Developer tools (hash, port finder, env checker, git stats)
- Bilingual documentation (English + Chinese)
- Optional dependency groups for minimal installs
- pytest test suite
```

- [ ] **Step 5: Commit**

```bash
git add README.md README_CN.md CONTRIBUTING.md CHANGELOG.md
git commit -m "docs: add comprehensive bilingual README, CONTRIBUTING, and CHANGELOG"
```

---

## Task 11: CI/CD and Cleanup

**Files:**
- Create: `.github/workflows/ci.yml`
- Remove: old directories (`good_codes/`, `tools/`, `notion_calendar/`, `files/`, `logs/`)

- [ ] **Step 1: Create GitHub Actions CI**

`.github/workflows/ci.yml`:
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Lint with ruff
        run: ruff check devkit/ tests/

      - name: Run tests
        run: pytest tests/ -v --tb=short
```

- [ ] **Step 2: Remove old directories**

```bash
git rm -r good_codes/ tools/ notion_calendar/ files/ logs/
```

Keep `docs/` (it has our specs and plans).

- [ ] **Step 3: Run full test suite**

Run: `pytest tests/ -v`
Expected: All tests pass.

- [ ] **Step 4: Final commit**

```bash
git add .github/ .gitignore
git add -u  # stage deletions
git commit -m "chore: add CI, remove legacy code, finalize v0.1.0 structure"
```

- [ ] **Step 5: Tag release**

```bash
git tag v0.1.0
```

---

## Summary

| Task | Description | New Files | Tests |
|------|-------------|-----------|-------|
| 1 | Project scaffolding | 12 | 3 |
| 2 | Shared utilities | 2 | 11 |
| 3 | Dev module | 5 | 10 |
| 4 | Files module | 5 | 7 |
| 5 | Data module | 4 | 10 |
| 6 | AI module | 4 | 8 |
| 7 | Text module | 5 | 7 |
| 8 | Web module | 3 | 5 |
| 9 | Convert module | 8 | 2 |
| 10 | Documentation | 4 | 0 |
| 11 | CI and cleanup | 1 | 0 |
| **Total** | | **53 files** | **63 tests** |

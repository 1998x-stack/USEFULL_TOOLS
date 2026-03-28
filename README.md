<div align="center">

# devkit

**A Swiss Army Knife for Developers**

27+ ready-to-use CLI tools for file conversion, text processing, AI/LLM utilities, data handling, and more.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-60%20passed-brightgreen)](tests/)

</div>

---

## Features

| Category | Tools | Description |
|----------|-------|-------------|
| **Convert** | 9 tools | PDF merge/compress, Markdown to PDF/DOCX, media conversion, image resize |
| **Text** | 4 tools | Information-entropy text length, keyword extraction, sentence splitting, tokenizer |
| **Files** | 4 tools | Duplicate finder, log search, code extractor, batch rename |
| **AI** | 4 tools | Token counter, prompt templates, cost calculator, model comparison |
| **Data** | 5 tools | JSON flatten/merge/query, CSV merge/split/convert, Excel to CSV |
| **Web** | 3 tools | QR code generate/read, URL validation with metadata |
| **Dev** | 4 tools | Hash tool, port finder, environment checker, git statistics |

---

## Quick Start

```bash
# Install core tools (zero dependencies beyond click)
pip install devkit-tools

# Install with all optional features
pip install devkit-tools[all]

# Or install specific feature groups
pip install devkit-tools[ai]       # Token counting, cost calculator
pip install devkit-tools[nlp]      # Chinese text processing
pip install devkit-tools[convert]  # PDF, DOCX, media conversion
pip install devkit-tools[data]     # Excel support
pip install devkit-tools[web]      # QR codes, URL metadata
```

```bash
# Try it out
devkit --help
devkit dev hash "Hello, World!"
devkit dev ports --range 3000-9000
devkit text length "Hello 你好 World"
devkit ai cost --model gpt-4o --input-tokens 1000 --output-tokens 500
```

---

## Installation

### From PyPI

```bash
pip install devkit-tools
```

### From Source

```bash
git clone https://github.com/yourusername/devkit.git
cd devkit
pip install -e ".[all]"
```

### Development Setup

```bash
git clone https://github.com/yourusername/devkit.git
cd devkit
pip install -e ".[all]"
pip install -r requirements-dev.txt
pytest tests/ -v
```

---

## Tool Reference

<details>
<summary><b>Convert - Document & Media Conversion (9 tools)</b></summary>

### Convert Tools

| Command | Description | Example |
|---------|-------------|---------|
| `convert pdf-merge` | Merge all PDFs in a directory | `devkit convert pdf-merge ./pdfs -o merged.pdf` |
| `convert pdf-compress` | Compress PDF via Ghostscript | `devkit convert pdf-compress large.pdf --quality ebook` |
| `convert md2pdf` | Markdown to PDF | `devkit convert md2pdf README.md -o readme.pdf` |
| `convert md2docx` | Markdown to DOCX | `devkit convert md2docx README.md -o readme.docx` |
| `convert mp4-to-mp3` | Extract audio from video | `devkit convert mp4-to-mp3 video.mp4` |
| `convert webp-to-png` | WebP to PNG conversion | `devkit convert webp-to-png image.webp` |
| `convert resize` | Resize images | `devkit convert resize photo.jpg 800x600` |
| `convert doc` | Convert between document formats | `devkit convert doc report.docx --to pdf` |

#### System Requirements

Some conversion tools require external programs:

- **PDF compress:** [Ghostscript](https://ghostscript.com/) (`gs`)
- **MP4 to MP3:** [FFmpeg](https://ffmpeg.org/) (`ffmpeg`)
- **Doc convert:** [LibreOffice](https://www.libreoffice.org/) and/or [Pandoc](https://pandoc.org/)

#### Examples

```bash
# Merge all PDFs in a folder
devkit convert pdf-merge ./documents -o combined.pdf

# Compress a PDF for email
devkit convert pdf-compress thesis.pdf --quality ebook

# Convert Markdown to Word document
devkit convert md2docx notes.md -o notes.docx

# Resize an image to 300x300
devkit convert resize photo.jpg 300

# Convert between document formats
devkit convert doc report.docx --to pdf
```

</details>

<details>
<summary><b>Text - Text & NLP Processing (4 tools)</b></summary>

### Text Tools

| Command | Description | Example |
|---------|-------------|---------|
| `text length` | Information-entropy weighted text length | `devkit text length "Hello 你好"` |
| `text keywords` | Extract weighted keywords (CN/EN) | `devkit text keywords "your text" --lang en` |
| `text split` | Split Chinese text into sentences | `devkit text split "第一句。第二句。"` |
| `text char-count` | Count characters by category | `devkit text char-count "Hello 你好 123"` |

#### How Text Length Works

Unlike simple `len()`, this tool uses information-entropy weighting:

| Character Type | Weight | Rationale |
|---------------|--------|-----------|
| CJK characters | 1.0 | High information density |
| English words | 0.47 | Semantic unit |
| Digits | 0.01 | Low entropy |
| Spaces | 0.001 | Formatting only |
| Punctuation | 0.05 | Structural |
| Emoji | 0.2 | Visual meaning |

#### Examples

```bash
# Calculate weighted text length
devkit text length "Hello World"
# Output: Weighted length: 0

devkit text length "你好世界"
# Output: Weighted length: 4

# Extract keywords from English text
devkit text keywords "Python is a great programming language" --lang en --top 5

# Split Chinese text into sentences
devkit text split "今天天气很好。我们去公园吧。" --criterion coarse

# Count character types
devkit text char-count "Hello 你好 123"
```

</details>

<details>
<summary><b>Files - File Management (4 tools)</b></summary>

### Files Tools

| Command | Description | Example |
|---------|-------------|---------|
| `files dedup` | Find and remove duplicate files | `devkit files dedup ./downloads --extensions pdf,mp3` |
| `files search` | Search text in files | `devkit files search app.log "ERROR"` |
| `files extract-code` | Extract and merge source code | `devkit files extract-code ./src -o all_code.txt` |
| `files rename` | Batch rename with patterns | `devkit files rename ./photos --pattern "img_{n:03d}.jpg"` |

#### Examples

```bash
# Find duplicate files (dry run by default)
devkit files dedup ./downloads --extensions pdf,mp3,mp4

# Actually remove duplicates
devkit files dedup ./downloads --execute

# Search log files
devkit files search server.log "timeout" --context 5

# Extract all Python code into one file
devkit files extract-code ./project -o combined.py --extensions py

# Preview batch rename
devkit files rename ./photos --pattern "vacation_{n:03d}.jpg"

# Execute batch rename
devkit files rename ./photos --pattern "vacation_{n:03d}.jpg" --execute
```

</details>

<details>
<summary><b>AI - AI/LLM Utilities (4 tools)</b></summary>

### AI Tools

| Command | Description | Example |
|---------|-------------|---------|
| `ai tokens` | Count tokens for LLM models | `devkit ai tokens "Hello world" --model gpt-4o` |
| `ai cost` | Estimate API cost | `devkit ai cost --model gpt-4o --input-tokens 1000 --output-tokens 500` |
| `ai cost-compare` | Compare costs across models | `devkit ai cost-compare --input-tokens 10000 --output-tokens 5000` |
| `ai prompt` | Manage prompt templates | `devkit ai prompt my-template --vars '{"name": "World"}'` |

#### Supported Models

| Provider | Models |
|----------|--------|
| OpenAI | gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-4, gpt-3.5-turbo |
| Anthropic | claude-opus, claude-sonnet, claude-haiku |
| Google | gemini-pro, gemini-flash |

#### Examples

```bash
# Count tokens in a file
devkit ai tokens README.md --file --model gpt-4o

# Estimate cost for a conversation
devkit ai cost --model claude-sonnet --input-tokens 5000 --output-tokens 2000
# Output: Estimated cost for claude-sonnet: $0.045000

# Compare costs across all models
devkit ai cost-compare --input-tokens 10000 --output-tokens 5000

# Save a prompt template
devkit ai prompt greeting --save "Hello, {name}! Welcome to {project}."

# Use a saved template
devkit ai prompt greeting --vars '{"name": "Alice", "project": "devkit"}'
```

</details>

<details>
<summary><b>Data - Data Processing (5 tools)</b></summary>

### Data Tools

| Command | Description | Example |
|---------|-------------|---------|
| `data json-flatten` | Flatten nested JSON | `devkit data json-flatten config.json` |
| `data json-merge` | Merge JSONL files | `devkit data json-merge a.jsonl b.jsonl -o merged.jsonl` |
| `data csv-merge` | Merge CSV files | `devkit data csv-merge jan.csv feb.csv -o combined.csv` |
| `data csv-split` | Split large CSV files | `devkit data csv-split big.csv --rows 1000` |
| `data excel2csv` | Convert Excel to CSV | `devkit data excel2csv report.xlsx -o report.csv` |

#### Examples

```bash
# Flatten nested JSON for analysis
devkit data json-flatten api_response.json -o flat.json
# {"user.name": "Alice", "user.address.city": "NYC"} ...

# Merge multiple JSONL files
devkit data json-merge logs_jan.jsonl logs_feb.jsonl -o all_logs.jsonl

# Merge CSV files with same headers
devkit data csv-merge q1.csv q2.csv q3.csv q4.csv -o annual.csv

# Split a large CSV into 1000-row chunks
devkit data csv-split users.csv --rows 1000 -o ./chunks/

# Convert Excel spreadsheet to CSV
devkit data excel2csv report.xlsx --sheet "Sales" -o sales.csv
```

</details>

<details>
<summary><b>Web - Web Utilities (3 tools)</b></summary>

### Web Tools

| Command | Description | Example |
|---------|-------------|---------|
| `web qrcode` | Generate QR code image | `devkit web qrcode "https://github.com" -o qr.png` |
| `web qrcode-read` | Read QR code from image | `devkit web qrcode-read qr.png` |
| `web validate-url` | Validate URL with metadata | `devkit web validate-url "https://example.com" --metadata` |

#### Examples

```bash
# Generate a QR code
devkit web qrcode "https://github.com/yourusername/devkit" -o github_qr.png --size 400

# Read a QR code from an image
devkit web qrcode-read screenshot.png

# Validate a URL and fetch metadata
devkit web validate-url "https://github.com" --metadata
```

</details>

<details>
<summary><b>Dev - Developer Utilities (4 tools)</b></summary>

### Dev Tools

| Command | Description | Example |
|---------|-------------|---------|
| `dev hash` | Hash strings or files | `devkit dev hash "password123" --algo sha256` |
| `dev ports` | Find available network ports | `devkit dev ports --range 3000-9000 --count 5` |
| `dev env-check` | Check dev environment | `devkit dev env-check --tools python,node,git,docker` |
| `dev git-stats` | Git repository statistics | `devkit dev git-stats --path .` |

#### Examples

```bash
# Hash a string
devkit dev hash "Hello, World!" --algo sha256
# Output: dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f

# Hash a file
devkit dev hash package.json --algo md5 --file

# Find available ports
devkit dev ports --range 8000-9000 --count 3

# Check development environment
devkit dev env-check --tools python,node,git,docker,ffmpeg

# Get git repository statistics
devkit dev git-stats
```

</details>

---

## Library Usage

All tools are also importable as Python modules:

```python
from devkit.text import calculate_custom_length, split_sentence
from devkit.data import flatten_json, merge_csvs
from devkit.dev.hash_tool import hash_string, hash_file
from devkit.ai.cost_calculator import compare_costs

# Calculate information-weighted text length
length = calculate_custom_length("Hello 你好 World")

# Flatten nested JSON
flat = flatten_json({"a": {"b": {"c": 1}}})
# {"a.b.c": 1}

# Compare LLM API costs
costs = compare_costs(input_tokens=10000, output_tokens=5000)
```

---

## Project Structure

```
devkit/
├── cli.py              # Click-based CLI entry point
├── utils.py            # Shared utilities
├── convert/            # Document & media conversion
├── text/               # Text & NLP processing
├── files/              # File management
├── ai/                 # AI/LLM utilities
├── data/               # Data processing
├── web/                # Web utilities
└── dev/                # Developer utilities

tests/                  # pytest test suite (60 tests)
examples/sample_data/   # Sample files for testing
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

---

<div align="center">

## 中文说明

</div>

### 简介

**devkit** 是一个面向开发者的多功能命令行工具集，包含 27+ 个即用型工具，涵盖文件转换、文本处理、AI/LLM 工具、数据处理等多个领域。

### 安装

```bash
# 安装核心工具
pip install devkit-tools

# 安装所有功能
pip install devkit-tools[all]
```

### 工具分类

| 分类 | 工具数 | 说明 |
|------|--------|------|
| **转换 (Convert)** | 9 | PDF 合并/压缩、Markdown 转 PDF/DOCX、媒体转换 |
| **文本 (Text)** | 4 | 信息熵文本长度、关键词提取、中文分句、分词器 |
| **文件 (Files)** | 4 | 重复文件查找、日志搜索、代码提取、批量重命名 |
| **AI** | 4 | Token 计数、Prompt 模板、费用计算器 |
| **数据 (Data)** | 5 | JSON 扁平化/合并/查询、CSV 合并/拆分、Excel 转 CSV |
| **网络 (Web)** | 3 | 二维码生成/识别、URL 验证 |
| **开发 (Dev)** | 4 | 哈希工具、端口查找、环境检查、Git 统计 |

### 使用示例

```bash
# 计算文本信息熵长度
devkit text length "你好世界"

# 提取关键词
devkit text keywords "自然语言处理是人工智能的重要方向" --lang zh

# 中文分句
devkit text split "第一句话。第二句话。第三句话。"

# 比较 LLM API 费用
devkit ai cost-compare --input-tokens 10000 --output-tokens 5000

# 合并 CSV 文件
devkit data csv-merge data1.csv data2.csv -o combined.csv
```

完整中文文档请参阅 [README_CN.md](README_CN.md)。

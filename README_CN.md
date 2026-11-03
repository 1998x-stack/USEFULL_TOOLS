<div align="center">

# devkit

**开发者的瑞士军刀**

27+ 个即用型命令行工具，涵盖文件转换、文本处理、AI/LLM 工具、数据处理等多个领域。

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## 安装

> **注意：** PyPI 上的 `devkit-tools` 是其他项目，不是本仓库的发行包。请从源码安装，详见 [安全说明](docs/SAFETY.md)。


```bash
# 获取源码
git clone https://github.com/1998x-stack/USEFULL_TOOLS.git
cd USEFULL_TOOLS

# 安装核心工具
python -m pip install -e .

# 安装所有功能
python -m pip install -e ".[all]"

# 按需安装
python -m pip install -e ".[ai]"       # Token 计数、费用计算
python -m pip install -e ".[nlp]"      # 中文文本处理
python -m pip install -e ".[convert]"  # PDF、DOCX、媒体转换
python -m pip install -e ".[data]"     # Excel 支持
python -m pip install -e ".[web]"      # 二维码、URL 元数据
```

---

## 当前功能与文档

**V0.4-A～E 已合并到 `main`。** 包元数据仍为 `0.1.0`，并不表示已经通过 PyPI 发布了新的版本。
本仓库的 `devkit-tools` 与 PyPI 上的同名项目不同；请按照下方源码安装命令操作。

- [文档总览](docs/README.md) · [V0.3 数据契约](docs/data-contracts-v0.3.md)
- [V0.4 转换架构](docs/conversion-v0.4.md) · [DOCX 结构保真](docs/conversion-v0.4b.md)
- [中文 PDF 与字体](docs/conversion-v0.4c.md) · [视觉黄金基线](docs/conversion-v0.4d.md)
- [质量模式、Python API 与报告](docs/conversion-v0.4e.md) · [报告 JSON Schema](schemas/conversion-report-v1.schema.json)

### 系统依赖

`.[convert]` 仅安装 Python 库。Markdown → DOCX 需要 **Pandoc**；
Markdown → PDF 还需要 **LibreOffice Writer**；中文、日文等 PDF 还需要系统中的
**fontconfig 与 CJK 字体**。PDF 压缩另需 Ghostscript；MP4 转 MP3 另需 FFmpeg。

Ubuntu 示例：

```bash
python -m pip install -e ".[convert]"
sudo apt-get update
sudo apt-get install -y pandoc libreoffice-writer fontconfig fonts-noto-cjk
```

其他系统需要自行安装对应的可执行程序和字体；不同系统的字体渲染效果不能默认视为完全一致。

### 文档转换质量等级

| 等级 | Markdown → DOCX | Markdown → PDF |
|---|---|---|
| `fast` | 格式有效；保留转换器的必需检查 | 格式有效；保留必需的文本与图片安全检查 |
| `standard`（默认） | 独立检查 OOXML 结构，报告 L2 | 检查 Unicode、图片、缺字与页面边界，报告 L2 |
| `strict` | 额外进行格式和文本回读，最高 L2 | 必须匹配审核过的固定输入、截图和渲染环境，才报告 L3 |

严格模式缺少经审核的基线时**必须失败**，不会自动放宽验证。它不能保证任意文档在所有系统上视觉完全一致。

```bash
# 使用仓库内 Markdown 样例生成并验证 DOCX
devkit convert md2docx examples/sample_data/sample.md \
  --profile standard -o /tmp/sample.docx --report /tmp/docx-quality.json

# 生成 PDF 并保存质量报告
devkit convert md2pdf examples/sample_data/sample.md \
  --profile standard -o /tmp/sample.pdf --report /tmp/pdf-quality.json

# 只读检查已生成的 Word 文档，不重新渲染、不修改输出
devkit convert audit examples/sample_data/sample.md /tmp/sample.docx \
  --profile standard --report /tmp/recheck.json
```

严格 PDF 示例、不可变黄金截图和报告字段详见 [V0.4-E 文档](docs/conversion-v0.4e.md)。
## 工具分类

### 转换工具 (Convert) - 9 个工具

| 命令 | 说明 | 示例 |
|------|------|------|
| `convert pdf-merge` | 合并目录中的 PDF | `devkit convert pdf-merge ./pdfs -o merged.pdf` |
| `convert pdf-compress` | 压缩 PDF | `devkit convert pdf-compress large.pdf --quality ebook` |
| `convert md2pdf` | Markdown 转 PDF | `devkit convert md2pdf README.md` |
| `convert md2docx` | Markdown 转 DOCX | `devkit convert md2docx README.md` |
| `convert mp4-to-mp3` | 视频提取音频 | `devkit convert mp4-to-mp3 video.mp4` |
| `convert webp-to-png` | WebP 转 PNG | `devkit convert webp-to-png image.webp` |
| `convert resize` | 调整图片大小 | `devkit convert resize photo.jpg 800x600` |
| `convert doc` | 统一格式转换与质量检查 | `devkit convert doc notes.md --to pdf --profile standard` |
| `convert audit` | 对已有输出进行只读审核 | `devkit convert audit notes.md notes.docx --profile standard` |

### 文本工具 (Text) - 4 个工具

| 命令 | 说明 | 示例 |
|------|------|------|
| `text length` | 信息熵加权文本长度 | `devkit text length "你好世界"` |
| `text keywords` | 加权关键词提取 | `devkit text keywords "文本内容" --lang zh` |
| `text split` | 中文分句 | `devkit text split "第一句。第二句。"` |
| `text char-count` | 分类字符统计 | `devkit text char-count "Hello 你好"` |

### 文件工具 (Files) - 4 个工具

| 命令 | 说明 | 示例 |
|------|------|------|
| `files dedup` | 查找并删除重复文件 | `devkit files dedup ./downloads` |
| `files search` | 搜索文件内容 | `devkit files search app.log "ERROR"` |
| `files extract-code` | 提取合并源代码 | `devkit files extract-code ./src -o code.txt` |
| `files rename` | 批量重命名 | `devkit files rename ./photos --pattern "img_{n:03d}.jpg"` |

### AI 工具 - 4 个工具

| 命令 | 说明 | 示例 |
|------|------|------|
| `ai tokens` | LLM Token 计数 | `devkit ai tokens "文本" --model gpt-4o` |
| `ai cost` | API 费用估算 | `devkit ai cost --model gpt-4o --input-tokens 1000 --output-tokens 500` |
| `ai cost-compare` | 跨模型费用对比 | `devkit ai cost-compare --input-tokens 10000 --output-tokens 5000` |
| `ai prompt` | Prompt 模板管理 | `devkit ai prompt my-template` |

### 数据工具 (Data) - 5 个工具

| 命令 | 说明 | 示例 |
|------|------|------|
| `data json-flatten` | JSON 扁平化 | `devkit data json-flatten config.json` |
| `data json-merge` | 合并 JSONL 文件 | `devkit data json-merge a.jsonl b.jsonl -o merged.jsonl` |
| `data csv-merge` | 合并 CSV 文件 | `devkit data csv-merge a.csv b.csv -o combined.csv` |
| `data csv-split` | 拆分大型 CSV | `devkit data csv-split big.csv --rows 1000` |
| `data excel2csv` | Excel 转 CSV | `devkit data excel2csv report.xlsx` |

### 网络工具 (Web) - 3 个工具

| 命令 | 说明 | 示例 |
|------|------|------|
| `web qrcode` | 生成二维码 | `devkit web qrcode "https://github.com" -o qr.png` |
| `web qrcode-read` | 识别二维码 | `devkit web qrcode-read qr.png` |
| `web validate-url` | URL 验证 | `devkit web validate-url "https://example.com"` |

### 开发工具 (Dev) - 4 个工具

| 命令 | 说明 | 示例 |
|------|------|------|
| `dev hash` | 哈希计算 | `devkit dev hash "text" --algo sha256` |
| `dev ports` | 查找可用端口 | `devkit dev ports --range 3000-9000` |
| `dev env-check` | 开发环境检查 | `devkit dev env-check --tools python,node,git` |
| `dev git-stats` | Git 仓库统计 | `devkit dev git-stats` |

---

## 作为 Python 库使用

```python
from devkit.text import calculate_custom_length, split_sentence
from devkit.data import flatten_json
from devkit.ai.cost_calculator import compare_costs

# 计算信息熵加权文本长度
length = calculate_custom_length("你好世界")  # 4

# JSON 扁平化
flat = flatten_json({"a": {"b": {"c": 1}}})  # {"a.b.c": 1}

# LLM 费用对比
costs = compare_costs(input_tokens=10000, output_tokens=5000)
```

---

## 贡献

欢迎贡献！请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

MIT License - 详见 [LICENSE](LICENSE)。

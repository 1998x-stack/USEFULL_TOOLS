<div align="center">

# devkit

**开发者的瑞士军刀**

27+ 个即用型命令行工具，涵盖文件转换、文本处理、AI/LLM 工具、数据处理等多个领域。

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## 安装

```bash
# 安装核心工具
pip install devkit-tools

# 安装所有功能
pip install devkit-tools[all]

# 按需安装
pip install devkit-tools[ai]       # Token 计数、费用计算
pip install devkit-tools[nlp]      # 中文文本处理
pip install devkit-tools[convert]  # PDF、DOCX、媒体转换
pip install devkit-tools[data]     # Excel 支持
pip install devkit-tools[web]      # 二维码、URL 元数据
```

---

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
| `convert doc` | 文档格式转换 | `devkit convert doc report.docx --to pdf` |

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

# Documentation index

This repository contains the devkit CLI. `main` includes the V0.2 file-safety,
V0.3 data-correctness and V0.4 conversion-fidelity source milestones.
Distribution metadata still declares version `0.1.0`; this does not imply
a newly published PyPI release.

## Getting started

| Document | Purpose |
|---|---|
| [English README](../README.md) | Installation, commands and examples |
| [中文 README](../README_CN.md) | 中文安装、工具使用、转换质量模式 |
| [Contributing](../CONTRIBUTING.md) | Developer setup, testing, golden approval |
| [Safety](SAFETY.md) | File operation safeguards and publication boundaries |
| [Troubleshooting](TROUBLESHOOTING.md) | Missing backends, font issues, quality failures |

## Technical contracts

| Topic | Reference |
|---|---|
| CSV, JSON and Excel validation | [V0.3 data contracts](data-contracts-v0.3.md) |
| Conversion architecture and L1/L2/L3 | [V0.4 architecture](conversion-v0.4.md) |
| Pandoc AST, DocumentIR and DOCX | [V0.4-B](conversion-v0.4b.md) |
| CJK PDF, fonts and text checks | [V0.4-C](conversion-v0.4c.md) |
| Six approved PNG baselines and review protocol | [V0.4-D](conversion-v0.4d.md) |
| Quality profiles, CLI, Python API and audit | [V0.4-E](conversion-v0.4e.md) |
| Quality report fields | [JSON Schema v1](../schemas/conversion-report-v1.schema.json) |

## Verification

```bash
ruff check devkit/ tests/
pytest tests/ -m "not pdf_integration and not visual_integration"
```

The real CJK/PDF and read-only visual golden CI jobs run separately with
system Pandoc, LibreOffice, fontconfig and installed fonts. Approved
test fixtures live under `../tests/fixtures/visual_v04d/`; never
silently regenerate reviewed golden PNGs from failed CI output.

Implementation history: [merged PR #7](https://github.com/1998x-stack/USEFULL_TOOLS/pull/7).

# V0.4 — Document Conversion Fidelity

**Status:** V0.4-A through V0.4-E are merged into `main` through
[PR #7](https://github.com/1998x-stack/USEFULL_TOOLS/pull/7).
These are **repository features**, not a newly published distribution:
`pyproject.toml` still declares version `0.1.0`.

## Quality contract

| Level | Meaning | Supporting evidence |
|---|---|---|
| L1 — Valid | Parseable file and safe single-output publication | PDF page count / DOCX package check |
| L2 — Structural and content | Supported headings, tables, images, links, glyphs and text checks | Original Pandoc AST, independent OOXML/PDF checks |
| L3 — Approved visual regression | A **specific** reviewed source renders like its fixed reference | Locked renderer/font versions, SHA-256 PNGs, page/region diffs |

L3 requires a byte-identical approved Markdown fixture and matching
renderer/font environment; it is **not** a general visual guarantee.
Strict DOCX can achieve L2 but not L3. Word → PDF / Markdown currently
establish L1 (including with the `standard` profile).

## Implemented architecture

```text
devkit/convert/
  _safe.py                 # alias checks, safe single-file publication
  doc_convert.py           # isolated LibreOffice and Pandoc adapters
  engines/pandoc.py        # Markdown/Word backend bridge
  ir/pandoc.py             # typed DocumentIR projection + original AST
  md2docx.py              # Markdown → validated DOCX
  fonts.py                # fontconfig discovery, CMap coverage preflight
  reference_doc.py        # full Pandoc Word template with East Asian fonts
  md2pdf.py               # Markdown → Pandoc DOCX → LibreOffice PDF
  pdf_merge.py            # pypdf merging
  pdf_compress.py         # checked Ghostscript compression
  validate/structure.py   # independent DOCX OOXML checks
  validate/pdf_quality.py # Unicode, image, glyph and page bounds checks
  visual.py               # screenshot and region regression engine
  visual_cli.py           # reviewed-candidate versus read-only verify
  quality.py              # fast/standard/strict and JSON evidence
```

The complete Pandoc JSON AST is preserved during rendering.
DocumentIR is an inspectable, typed projection; it does not claim to
fully model every Markdown or Word construct.

## Stages delivered

| Phase | Implementation | Documentation |
|---|---|---|
| A | Safe output, isolated LibreOffice, PDF validation, pypdf | [Safety](SAFETY.md) |
| B | Pandoc AST, DocumentIR, OOXML DOCX tests | [V0.4-B](conversion-v0.4b.md) |
| C | CJK font checks, PDF text/images/geometry | [V0.4-C](conversion-v0.4c.md) |
| D | Six approved visual PNGs with region/pagination checks | [V0.4-D](conversion-v0.4d.md) |
| E | Quality profiles, read-only audit, JSON Schema | [V0.4-E](conversion-v0.4e.md) |

Historical stacked PRs #3–#6 were closed; all V0.4 features were
integrated into merged PR #7.

## Supported routes

| Input → output | Implementation | Current proven quality level |
|---|---|---|
| Markdown → DOCX | Pandoc and independent OOXML checks | L1 fast; L2 standard/strict |
| Markdown → PDF | Pandoc → DOCX → LibreOffice + PyMuPDF | L1 fast; L2 standard; L3 approved strict fixture |
| Word DOC/DOCX → PDF | LibreOffice | L1 |
| Word DOC/DOCX → Markdown | Pandoc | L1 |
| Multiple PDFs → merged PDF | pypdf | Validated output and pages |
| PDF → compressed PDF | Ghostscript | Validated file/page count, not guaranteed smaller |

## Getting started

```bash
git clone https://github.com/1998x-stack/USEFULL_TOOLS.git
cd USEFULL_TOOLS
python -m pip install -e ".[convert]"
sudo apt-get update
sudo apt-get install -y pandoc libreoffice-writer fontconfig fonts-noto-cjk

devkit convert md2docx examples/sample_data/sample.md -o /tmp/sample.docx \
  --profile standard --report /tmp/docx-quality.json
devkit convert audit examples/sample_data/sample.md /tmp/sample.docx \
  --profile standard --report /tmp/read-only-audit.json
```

The apt commands apply to Ubuntu. Other systems need independently
installed Pandoc, LibreOffice and appropriate fonts. Pip extras do not
install system converter binaries.

## Evidence boundaries

- Python 3.9–3.12 tests include real Pandoc DOCX and prior file/data regressions.
- Real CJK PDF tests use LibreOffice, Pandoc, fontconfig and installed CJK fonts.
- Ubuntu 24.04 CI verifies approved six-PNG/renderer-lock golden references.
- Approved goldens cover **two synthetic Markdown documents**, not all
  possible documents. A PDF text recall metric is not an assurance of
  correct reading order, pagination or accessibility tagging.

OCR, PDF/A, Word drawing, complex merged cells, advanced equations, RTL
and cross-platform pixel-perfect layouts require further dedicated tests.

For usage and report shape, see [V0.4-E](conversion-v0.4e.md);
for common failures, see [Troubleshooting](TROUBLESHOOTING.md).

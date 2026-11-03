# V0.4-E — Conversion quality profiles, audit API and JSON evidence

Release scope: V0.4-A/B/C/D/E in a single PR based on the **current main**,
preserving V0.3 validated data processing and its tests.

## Why profiles are explicit

| Profile | Markdown to DOCX | Markdown to PDF | Other Office formats |
|---|---|---|---|
| fast | L1, full mandatory renderer-level structural safety | L1, existing mandatory CJK/text/image safety | L1 output validity |
| standard | L2, independent OOXML heading/table/image/link audit | L2, extra Unicode recall/image/glyph/bounds audit | L1 only (no unfounded L2 claim) |
| strict | L2, plus bold/italic and independent Pandoc text recall | L3, **requires approved renderer/font/PDF screenshots** | Unsupported, fails closed |

Fast does NOT disable the Markdown converter's existing core integrity
checks. Strict DOCX never claims visual L3. PDF strict requires an explicit
golden fixture that is byte-identical to the source Markdown. An arbitrary
file cannot automatically pass visual L3 without independent approval.

PDF minimum recall: fast and standard 99.5%; strict 99.9%. The CLI
--min-text-recall parameter can only tighten a selected profile.

## Run examples

~~~bash
# Convert and save standard quality results
devkit convert md2docx notes.md -o notes.docx --profile standard --report notes.json
devkit convert md2pdf notes.md -o notes.pdf --profile standard --report notes.json

# Strict CJK PDF against a reviewed existing golden fixture
devkit convert md2pdf tests/fixtures/visual_v04d/cjk-layout.md \
  -o /tmp/approved.pdf --profile strict \
  --visual-manifest tests/fixtures/visual_v04d/manifest.json \
  --visual-case cjk-layout \
  --artifacts-dir /tmp/visual-evidence \
  --report /tmp/approved-quality.json

# Recheck an existing converted file without modifying it
devkit convert audit notes.md notes.docx --profile standard --report audit.json

# Unified convert route; md -> pdf now supported too
devkit convert doc notes.md --to pdf -o notes.pdf --profile fast
~~~

## Python API

~~~python
from devkit.convert.quality import (
    ConversionFailure, audit_existing, convert_with_quality,
)

try:
    result = convert_with_quality(
        "source.md", "docx", "output.docx",
        profile="standard", report_path="output.quality.json",
    )
    assert result.report.status == "passed"
except ConversionFailure as exc:
    print(exc.report.diagnostics)

quality = audit_existing("source.md", "output.docx")
print(quality.achieved_level)
~~~

## Data contract

See [Report JSON Schema v1](../schemas/conversion-report-v1.schema.json).
A report contains: schema_version, operation, profile, source/destination,
status, achieved_level (none, L1, L2, L3), per-gate checks with evidence,
numeric/structured metrics, diagnostic severity and code, backend pipeline,
and elapsed milliseconds. Raw Markdown/document contents are not embedded.

For conversion or gate failure, report status is failed, a diagnostic is
recorded, and any existing destination document remains unchanged. Strict PDF
is validated **before** publishing the final output.

The JSON report itself is atomically published as a separate file. Output
PDF/DOCX and the report JSON are NOT an atomic multi-file transaction:
if a report write fails after successful output publication, the output
remains published and the report I/O error propagates directly. Report
paths are not allowed to alias input or output, even via hard links.

The separate audit_existing API checks a previously converted file without
overwriting it or re-running Pandoc/LibreOffice to regenerate the output.

## Independent release checks

1. Existing V0.2/V0.3 tests must remain green on Python 3.9–3.12.
2. V0.4-A safe publication regressions and V0.4-B real DOCX goldens pass.
3. V0.4-C real Chinese/Japanese/PDF table-image tests pass on LibreOffice.
4. V0.4-D six independently reviewed binary PNG goldens are read-only
   verified against their SHA-256 hash manifest and engine/font lock.
5. V0.4-E quality profiles and failure reports are verified with fault
   injections and real PDF/DOCX integration tests.
6. A single consolidated PR diff is reviewed against the latest main;
   no old V0.3 implementation is restored.

## Explicit non-guarantees

V0.4 is not universal visual fidelity. It does not prove full accessibility
tagging, formula alignment, RTL, advanced Word drawing fidelity, complex
merged-cell preservation, PDF/A, or pixel-identical cross-platform rendering.
A locked visual golden validates only its approved fixture and environment.
Unsupported conversions or absent strict evidence must fail clearly.

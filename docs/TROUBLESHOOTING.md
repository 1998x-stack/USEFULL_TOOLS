# Troubleshooting document conversion

These instructions apply to this GitHub repository, **not** the unrelated
distribution using the same `devkit-tools` name on PyPI. This repository
still declares package version `0.1.0`.

## Required external tools

The `[convert]` extra installs Python libraries, not operating-system
executables.

| Symptom | Check | Resolution |
|---|---|---|
| Pandoc binary missing | `pandoc --version` | Install Pandoc for Markdown → DOCX / Word → Markdown |
| LibreOffice binary missing | `libreoffice --version` | Install Writer for Markdown → PDF / Word → PDF |
| No usable CJK font | `fc-match 'Noto Sans CJK SC'` | Install fontconfig and fonts covering source CJK characters |
| Ghostscript missing | `gs --version` | Install Ghostscript for PDF compression |
| FFmpeg missing | `ffmpeg -version` | Install FFmpeg for MP4 → MP3 |

Ubuntu example:

```bash
python -m pip install -e ".[convert]"
sudo apt-get update
sudo apt-get install -y pandoc libreoffice-writer fontconfig fonts-noto-cjk
```

Other systems require corresponding local programs and fonts; do not
assume identical rendering across operating systems. Never distribute
font binaries without the relevant permission.

## Failed quality check

Run a conversion with a separate JSON report path:

```bash
devkit convert md2docx examples/sample_data/sample.md \
  -o /tmp/sample.docx --profile standard --report /tmp/docx-quality.json
```

Inspect the JSON `status`, `profile`, `checks`, `metrics` and
`diagnostics` fields. A failure before final publication keeps the
previous output unchanged. Report destinations must not alias either
input or output (including existing hard links or symlinks).

Output and report are **separate atomic file publications**, not one
joint transaction. If report publication fails after an output succeeds,
the valid output remains published and the report I/O error propagates.

## Strict PDF baseline missing or environment mismatch

This failure is deliberate. Strict PDF requires:

- An approved manifest passed through `--visual-manifest`.
- An approved case ID passed through `--visual-case`.
- An evidence directory passed through `--artifacts-dir`.
- Source Markdown with **identical bytes** to the approved fixture.
- A renderer and installed CJK font matching the approved lock file.

For arbitrary Markdown, prefer `--profile standard` rather than
trying to fake or bypass the approved strict baseline. Strict DOCX
evaluates L2 structure and text, not L3 pixel fidelity.

## Visual regression after changing fonts or LibreOffice

Inspect the CI artifact's HTML, JSON, actual page PNGs and red-highlighted
difference PNGs. Verify page counts, table columns, image placement and
the final-page sentinel before approving any intended changes.

Prepare new candidate screenshots *manually*:

```bash
python -m devkit.convert.visual_cli candidate \
  --manifest tests/fixtures/visual_v04d/manifest.json \
  --out-dir /tmp/golden-candidates
```

Review and approve a separate commit containing the new PNGs, SHA-256
hashes, page counts and renderer/font lock. Normal CI runs read-only
`verify`, never self-approval.

## Audit an existing result without re-rendering

```bash
devkit convert audit examples/sample_data/sample.md /tmp/sample.docx \
  --profile standard --report /tmp/audit-report.json
```

This does not modify the converted document. See
[Quality profiles](conversion-v0.4e.md),
[Visual golden review](conversion-v0.4d.md) and
[Documentation index](README.md).

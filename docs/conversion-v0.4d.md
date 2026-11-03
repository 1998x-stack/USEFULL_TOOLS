# V0.4-D — Approved Visual Golden Dataset and Regression Gate

Status: implemented on stacked PR #6, based on V0.4-C PR #5 (in turn PR #4 and #3).

## Objective

Detect real Markdown-to-PDF visual regressions that cannot be established by a
parseable output, text recall, image counts or off-page bounding boxes alone.
Specifically detect header shifts, table/image region drift, overlap of text
lines, page count changes, missing last-page content and multi-page layout.

## Independent golden corpus

- `cjk-layout.md`: Chinese / Japanese / English, rich inline text, GFM table,
  embedded original project-owned chart PNG, quotation and several headings.
- `pagination.md`: 72 varied paragraphs, section headings, closing sentinel
  and repeated multi-page flow.
- `manifest.json`: fixed DPI, RGB comparison tolerance, expected page counts,
  named normalized page regions and approved PNG SHA-256 hashes.
- `approved/`: reviewed PNG images, **checked in as binary files** only after
  an independent inspection and separate approval commit.
- `baseline.lock.json`: locked Pandoc, LibreOffice, PyMuPDF versions, font
  family/index and installed font-file SHA-256. The host absolute font path
  is deliberately omitted.

No user/private/confidential documents are used. Generated assets are not
provided by copyrighted third-party sources. The source chart is a synthetic
diagram authored specifically for the fixture.

## Two strictly separated workflows

**Prepare candidate (NEVER approves):**

    python -m devkit.convert.visual_cli candidate \
      --manifest tests/fixtures/visual_v04d/manifest.json \
      --out-dir /tmp/candidate-goldens

The candidate output includes PNGs, intermediate rendered PDFs, and JSON/HTML
reports. The CI candidate job can emit base64 PNG blobs for controlled
review/approval; this option is not available in verification mode.

**Verify approved baseline (read-only):**

    python -m devkit.convert.visual_cli verify \
      --manifest tests/fixtures/visual_v04d/manifest.json \
      --out-dir /tmp/visual-comparison

A failure returns a nonzero exit code. The comparison writes its report and
red-highlighted diagnostic PNGs into the dedicated artifact directory. It
never alters the approved baseline images or manifest.

An approval requires a maintainer to inspect the candidate pages and diffs,
update or add the actual binary `approved/` PNGs, record their SHA-256 digests
and exact approved page counts, update `baseline.lock.json`, then submit a
separate audited Git commit. A CI job must never copy new candidate output
straight into `approved/` on a passing run.

## Evaluation layers

1. Prior V0.4-C PDF integrity gate: valid file, extractable Unicode text
   recall, embedded images, glyph replacement and off-page characters.
2. Render every page at 96 DPI using deterministic PyMuPDF RGB, alpha=False,
   annots=False. Abort on pages > 5 million pixels or more than 8 pages.
3. Require exactly the approved number of pages for each fixture.
4. Compute per-page **changed fraction**: ratio of pixels with max RGB
   channel difference >= 28. Default maximum: 0.006 (0.6%).
5. Compute per-page **mean absolute error**: mean raw channel difference.
   Default maximum: 1.2 on the 0..255 scale.
6. Compare named regions with individually stricter thresholds; coordinates
   are normalized so they can be inspected and reviewed.
7. Inspect geometric overlap between distinct PDF text lines; reject
   substantive intersections occupying >= 25% of a smaller line's box.
8. Save page-level actual and red-highlighted difference screenshots,
   summary report JSON, and an HTML table linking those evidence files.
9. Before comparison, check the golden PNG bytes against the reviewed hashes
   and compare the recorded engine/font fingerprint. Missing snapshots or
   version drift are failures, not silent acceptance.

## Regression tests

Independent synthetic mutation tests intentionally alter approved images and
documents. Required failures include header displacement, localized table
changes, page-count drift, changed checksum, missing reference, wrong raster
dimensions, offscreen text overlap, and HTML injection into report strings.

The real integration job uses Ubuntu 24.04 and installs real LibreOffice
Writer, Pandoc and Noto CJK fonts, then evaluates the approved fixtures.
Python 3.9–3.12 regular jobs test the image comparator and report builder
without requiring a full LibreOffice installation.

## Caveats

This is a **visual snapshot regression** test, not a proof of semantic
equivalence. An unchanged screenshot can hide nonselectable text or invalid
reading order, which must be caught by the V0.4-C text and document checks.
Screen snapshots may change when LibreOffice, fonts, rasterizer or rendering
runtime changes; this should trigger explicit review and baseline rotation.
The baseline environment fingerprint is a reproducibility gate, not a
security guarantee. UI-style alignment or SSIM normalization would risk
hiding small but important positioning changes, so this version compares
unshifted pages. More sophisticated perceptual scores are future work.

## PR workflow

- PR #3: V0.4-A baseline conversion safety.
- PR #4: V0.4-B Pandoc AST + structure-aware DOCX.
- PR #5: V0.4-C CJK-aware PDF and content/raster checks.
- PR #6: V0.4-D immutable visual goldens, regional diagnostics and regression gate.

Each PR must be merged or rebased in dependency order. PR #6 is considered
fully accepted only when its approved snapshots are reviewed and its dedicated
read-only visual integration CI succeeds.

# V0.4-C — CJK-aware Markdown → PDF Renderer

Status: stacked implementation awaiting CI and review.

## Pipeline

1. Parse Markdown with existing Pandoc JSON reader and typed DocumentIR.
2. Check local image policy from V0.4-B; no remote media downloads.
3. Derive expected printable text independently from the original Pandoc AST.
4. Discover an installed CJK font with fontconfig. Verify its Unicode CMap with
   fonttools rather than trusting fontconfig's substituted family name.
5. Generate a temporary reference DOCX with CJK font hints and A4 page setup.
6. Reuse V0.4-B to render structural DOCX (tables, lists, images, links).
7. Reuse V0.4-A isolated LibreOffice Writer to convert DOCX → PDF.
8. Validate source PDF page integrity, extracted Unicode recall, PDF image count,
   replacement glyphs, text bounds, and raster visibility.
9. Publish final PDF atomically only when every quality gate passes.

The pipeline is a deliberate DOCX intermediate. It is not a direct ReportLab or
HTML layout engine and it does not execute a browser or fetch internet resources.

## API

~~~bash
devkit convert md2pdf input.md -o result.pdf
devkit convert md2pdf input.md --font-family "Noto Sans CJK SC" --min-text-recall 0.99
~~~

~~~python
from devkit.convert.md2pdf import markdown_to_pdf
from devkit.convert.validate.pdf_quality import inspect_pdf_quality

output = markdown_to_pdf("input.md", "result.pdf")
report = inspect_pdf_quality(output, expected_text="期望的文本")
print(report.as_dict())
~~~

Public positional arguments are unchanged. CJK requires installed fontconfig
and system fonts. The repository does not ship or expose font files. On
Ubuntu, a suitable option is fonts-noto-cjk.

## Supported V0.4-C quality checks

- **Unicode:** source AST to PDF character-multiset recall, NFKC normalization.
- **Glyphs:** reject U+FFFD and common visible square replacement characters.
- **CJK preflight:** inspect font CMap, abort if any needed Han/Kana/Hangul glyph missing.
- **Text bounds:** individual PDF text boxes must stay within page extents (2pt tolerance).
- **Graphics:** PDF image instances must not be fewer than Markdown image nodes.
- **Raster:** render each PDF page via PyMuPDF, flag entirely blank output.
- **Output safety:** failed validation leaves destination unchanged.
- **Operational:** Pandoc/LibreOffice subprocesses have timeouts and use a temporary workdir.

## Non-guarantees and next stage

- Character-count recall does not prove reading order, formula layout, semantic
  equivalence, or that two visual regions are identical.
- Text that never reaches PDF is detected by recall; off-page glyph detection
  cannot find invisible characters whose PDF streams were already removed.
- A font CMap containing a codepoint is only an initial preflight. Rendering
  engines can still choose another fallback font or alter glyph shapes.
- A raster with visible pixels can contain overlap, poor layout or missing
  background elements. V0.4-D will add human-reviewed and region-level
  visual golden baselines.
- Output page count is limited by default to 100 to bound validation work.
- Fontconfig discovery on Linux is tested in CI; other platforms require
  separately verified font and LibreOffice availability.
- The generated DOCX has no stable visual layout across OS/font/backend
  versions. CI pins the Ubuntu package environment for the integration job,
  and future V0.4-D will record installed engine versions and pixel baselines.
- SVG, remote media, mathematics, complex merged tables, RTL scripts and
  accessibility-tagged PDF do not have full fidelity guarantees in V0.4-C.

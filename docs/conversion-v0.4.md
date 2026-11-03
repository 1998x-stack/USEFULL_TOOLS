# V0.4 Document Conversion Fidelity — Design and Acceptance Plan

Status: incremental. V0.4-A is the initial independently reviewable conversion-safety change.

## Three-level product contract

L1 **Valid:** valid document format, accurate output path, independent integrity check,
expected PDF page count where applicable, safe output publication, bounded external processes.

L2 **Structural:** preserve headings, text runs, hyperlinks, lists, tables, images and
reading order. Explicitly report unsupported features instead of silently dropping them.

L3 **Visual:** render pages and inspect missing glyphs, page breaks, clipped content,
table alignment and figure positioning using versioned render baselines.

Generating a parseable file qualifies as L1 only; L2 and L3 require independent evidence.

## Verified baseline issues

- md2pdf removes HTML tags using regular expressions, dropping structural semantics.
- md2docx uses get_text on top-level elements, omitting inline styling, links and tables.
- Word→PDF did not honor arbitrary output filenames: LibreOffice chose the source basename.
- PDF merge would include prior output on a repeated run when output lived in the input directory.
- Ghostscript/LibreOffice output validation and execution limits were incomplete.
- PyPDF2 needs migration to maintained pypdf.
- pdf_parse is an unimplemented placeholder and should not be advertised as a working converter.

## Target modules

~~~text
devkit/convert/
  _safe.py                  # current L1 source aliases, PDF/DOCX checks, atomic output
  models.py                 # later request, outcome, diagnostics
  engines/
    pandoc.py               # later Pandoc AST and DOCX writing
    libreoffice.py          # later isolated renderer and subprocess policy
    pypdf_engine.py         # later page/bookmark/form policies
  ir/
    blocks.py               # later structured DocumentIR with inline runs
    markdown.py             # later Markdown AST -> IR
    docx.py                 # later OOXML -> IR
  validate/
    integrity.py            # L1 format checks
    structure.py            # L2 structural tests
    visual.py               # L3 render diffs / glyph checks
  doc_convert.py
  pdf_merge.py
  pdf_compress.py
  md2pdf.py
  md2docx.py
~~~

## PR sequence and acceptance

| PR | Topic | Gate |
|---|---|---|
| V0.4-A | Output safety, custom paths, isolated LO, pypdf migration | Valid output, no source overwrite, CI 3.9–3.12 |
| V0.4-B | Markdown intermediate structure and DOCX renderer | Heading, bold, hyperlinks, lists, code, tables, images golden cases |
| V0.4-C | Markdown/PDF renderer and CJK fonts | Text selectable and extractable, no missing Chinese glyphs |
| V0.4-D | Independent rendering and structural fixtures | Reproducible baseline and documented tolerated deviations |
| V0.4-E | Diagnostics and fidelity profiles | Explain engine, unsupported features and confidence/quality gates |

## Future DocumentIR data contract

~~~python
@dataclass(frozen=True)
class InlineRun:
    text: str
    bold: bool = False
    italic: bool = False
    link: str | None = None

@dataclass(frozen=True)
class Block:
    kind: str                      # heading|paragraph|list|table|image|code|quote
    source_ref: str                # stable source span within a document revision
    level: int = 0
    runs: tuple[InlineRun, ...] = ()
    children: tuple = ()
    attributes: dict = field(default_factory=dict)

@dataclass(frozen=True)
class DocumentIR:
    blocks: tuple[Block, ...]
    media: dict
    metadata: dict
~~~

Use typed, immutable value objects in the implementation with Python 3.9-compatible
type annotations. Table cells and column spans must remain structured, not flattened.
DocumentIR is a future component, not part of V0.4-A.

## Golden corpus design

- Multilingual: Chinese / English / Japanese, punctuation, numbers, Unicode.
- Structure: H1-H6, nested bullet/ordered lists, quotations and code.
- Tables: wrapped cells, variable widths and merged cells.
- Media: embedded images, captions and local asset links.
- Office: headers/footers, landscape sections, page breaks and style inheritance.
- Edge: empty documents, malformed/encrypted PDFs, process timeouts and overwrite hazards.

Build the corpus using synthetic or explicitly licensed inputs; never redistribute
private user files. Each fixture stores expected headings, paragraphs, table cells,
images, links and source text with a platform/engine/font manifest.

## Independent acceptance metrics (targets, not measured claims)

| Metric | Proposed target |
|---|---|
| Supported-feature structural match | >= 98% |
| Extractable-text recall | >= 99.5% |
| Missing glyphs in configured Chinese fixture | 0 |
| Integrity failures incorrectly reported as success | 0 |
| In-place destructive operations accepted | 0 |
| Unsupported feature classes with explicit diagnostics | 100% |

L3 uses fixed DPI/engine/font versions and region-level comparison, not pixel-perfect
agreements across every operating system. Inspect renders manually for golden
regressions that automated metrics cannot explain.

## Engines and safety boundary

- Maintained pypdf PdfWriter.append handles PDF merge; bookmarks/forms need their
  own policies and dedicated tests.
- Pandoc native AST and reference DOCX are preferred for rich Markdown to DOCX.
- Isolate LibreOffice UserInstallation and direct external output to a temporary
  workdir; verify the actual produced file before publishing.
- Configure a legitimate, reusable CJK font profile without committing proprietary
  font files to GitHub.
- Keep external conversions argument-array-only (no shell), enforce timeouts and
  user-visible errors; separate conversion from output publication.
- Atomic replacement covers one file on one filesystem, not concurrent process
  modifications, power loss, or multi-file transactions.

## Explicitly unaddressed by V0.4-A

Inline styles/tables/images in the current md2pdf/md2docx implementation,
visual regressions, PDF accessibility tagging, PDF/A, OCR, forms, and true
semantic/visual fidelity are future work. A successful L1 validation does not
imply those features survived conversion.

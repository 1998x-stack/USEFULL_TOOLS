# V0.4-B — Structure-aware Markdown → DOCX

Status: merged into `main` via [PR #7](https://github.com/1998x-stack/USEFULL_TOOLS/pull/7).

## Rationale

The legacy Markdown→HTML→BeautifulSoup→python-docx implementation loses
links, images, tables, styling and numbering. The replacement uses Pandoc's
native JSON document model for rendering and creates a typed, inspectable
DocumentIR projection for validation and future search/annotation features.

**Important:** DocumentIR is not used to regenerate a simplified Pandoc AST.
It retains the *entire* original Pandoc JSON, including nodes that the typed
projection does not yet interpret. This avoids silent loss during rendering.

## Dataflow

~~~text
Markdown file
    |
    v
Pandoc --from=gfm --to=json    [bounded command, no shell]
    |
    v
DocumentIR                     [typed blocks, inline runs, table rows/cells]
    |                             |                 |
    |                             +--> feature counts and image policy
    v
Pandoc --from=json --to=docx   [original AST, optional --reference-doc]
    |
    v
Temp DOCX
    |
    v
OOXML structural checks        [headings, tables, links and embedded pictures]
    |
    v
Atomic publication            [no output replacement on validation failure]
~~~

Both CLI paths use the same pipeline:
- devkit convert md2docx input.md -o output.docx
- devkit convert doc input.md --to docx -o output.docx

Both support --reference-doc custom-reference.docx, which sets Word page
and style settings. This is an explicit backend requirement: Pandoc must be
installed and discoverable on PATH. No silent lossy fallback is used.

## Source contracts

- Supported golden features: headings, paragraphs, bold, emphasis, hyperlinks,
  unordered and ordered nested lists, GFM pipe tables, code, embedded local PNG.
- Source AST is recorded as JSON with pandoc-api-version. No fixed AST schema
  version is baked in; the reader/writer use the same Pandoc executable.
- DocumentIR contains frozen InlineNode and BlockNode projections with
  structural source references and table row/column spans.
- Tables and complex cells are kept as nested blocks; original AST stays
  available even where the projection lacks a specialized representation.
- Remote and absolute image URLs are rejected. Relative images are restricted
  to the Markdown source directory tree; missing images are errors, not warnings.
- Remote hyperlinks are permitted: links do not trigger network fetches.
- Existing output files are untouched if parsing, rendering, asset checks or
  OOXML validation fail.
- Existing custom reference DOCX cannot also be the output destination.

## Independent verification

Pandoc is used for actual rendering in CI, not just as a mocked subprocess.
Golden fixture: tests/fixtures/conversion_v04b/rich.md, plus a generated local
PNG. The test suite opens the resulting DOCX using python-docx and inspects
OOXML directly for the hyperlink target, styles, table cells, numbering, and
embedded media.

The minimum converter integrity gate compares source AST node counts against
OOXML headings, tables, links and images. The merged `strict` DOCX profile
also checks bold/italic runs and Pandoc DOCX text read-back against the
source. This is **L2**, not visual L3. Full list-level semantics, complex
equations, CSS style parity and exact pagination are not guaranteed.

## API

~~~python
from devkit.convert.md2docx import markdown_to_docx
from devkit.convert.engines import PandocEngine

doc_ir = PandocEngine().parse_markdown("notes.md")
print(doc_ir.feature_count("Table"))
print(doc_ir.blocks[0].source_ref)
output_path = markdown_to_docx("notes.md", "notes.docx")
~~~

Compatibility: existing positional parameters continue working. The optional
keyword-only reference_doc is new. Missing Pandoc now reports an actionable
FileNotFoundError instead of generating a partially styled result.

## Known limitations and next work

- Structural validation is selective, not a full semantic equivalence proof.
- Lists are exercised by golden tests; strict DOCX additionally rejects
  missing bold/italic run counts, but full numbering-level parity remains unproven.
- GFM Markdown does not represent every possible Word feature, notably complex
  merged-table authoring or full pagination/style controls.
- Pandoc's native AST format can change across versions. Persist its
  pandoc-api-version and use the same binary to read/write each document.
- The new command executes Pandoc locally; image assets must be trusted input
  under the source directory. For processing hostile HTML/Markdown at scale,
  process isolation and memory limits should be added before a hosted service.
- CJK PDF rendering and approved PDF visual goldens are covered by V0.4-C/D;
  DOCX conversion itself does not claim a visual L3 baseline.

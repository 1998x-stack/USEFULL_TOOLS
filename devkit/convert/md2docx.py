"""Markdown to DOCX using Pandoc AST, typed DocumentIR and OOXML validation."""

import tempfile
from pathlib import Path
from typing import Optional

from devkit.convert._safe import publish_file, require_distinct
from devkit.convert.engines import PandocEngine
from devkit.convert.validate.structure import verify_docx_structure


def markdown_to_docx(
    input_path: str,
    output_path: Optional[str] = None,
    *,
    reference_doc: Optional[str] = None,
) -> str:
    """Convert Markdown preserving lists, tables, images and inline formatting.

    The Pandoc JSON AST is the lossless rendering contract. DocumentIR projects
    inspectable typed nodes, and independent OOXML validation protects against
    silent omission of supported elements.
    """
    source = Path(input_path).absolute()
    if not source.is_file():
        raise FileNotFoundError(str(source))
    destination = output_path or str(source.with_suffix(".docx"))
    input_paths = [str(source)]
    if reference_doc:
        input_paths.append(str(reference_doc))
    require_distinct(input_paths, destination)

    engine = PandocEngine()
    document = engine.parse_markdown(source)
    # Validate before writing: remote images may cause unintended HTTP access.
    engine.check_local_media(document, source)

    with tempfile.TemporaryDirectory(prefix="devkit-md2docx-") as directory:
        staged = Path(directory) / "result.docx"
        engine.write_docx(document, staged, source, reference_doc=reference_doc)

        def check(path):
            verify_docx_structure(path, document)

        return publish_file(staged, destination, input_paths, validator=check)

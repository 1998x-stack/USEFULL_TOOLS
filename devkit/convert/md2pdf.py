"""CJK-aware Markdown→PDF via structural DOCX and isolated LibreOffice."""

import tempfile
from pathlib import Path
from typing import Optional

from devkit.convert._safe import publish_file, require_distinct, validate_pdf
from devkit.convert.engines import PandocEngine
from devkit.convert.fonts import choose_cjk_font
from devkit.convert.md2docx import markdown_to_docx
from devkit.convert.reference_doc import build_reference_docx
from devkit.convert.validate.pdf_quality import expected_text_from_ast, inspect_pdf_quality


def markdown_to_pdf(
    input_path: str,
    output_path: Optional[str] = None,
    *,
    font_family: Optional[str] = None,
    min_text_recall: float = 0.995,
) -> str:
    """Produce a structurally rendered PDF with CJK glyph and layout checks.

    The original Pandoc AST is used to obtain an expectation independent of
    the generated DOCX. Never publish a PDF that fails the final quality gate.
    """
    source = Path(input_path).absolute()
    if not source.is_file():
        raise FileNotFoundError(str(source))
    destination = output_path or str(source.with_suffix(".pdf"))
    require_distinct([source], destination)
    engine = PandocEngine()
    document = engine.parse_markdown(source)
    engine.check_local_media(document, source)
    expected = expected_text_from_ast(document.to_pandoc_ast())
    font = choose_cjk_font(expected, preferred_family=font_family)

    with tempfile.TemporaryDirectory(prefix="devkit-cjkpdf-") as directory:
        root = Path(directory)
        reference = None
        if font is not None:
            reference = build_reference_docx(font, str(root / "reference.docx"))
        docx = root / "render.docx"
        pdf = root / "render.pdf"
        markdown_to_docx(str(source), str(docx), reference_doc=reference)

        from devkit.convert.doc_convert import convert_document

        produced = convert_document(str(docx), "pdf", str(pdf))
        if produced is None:
            raise RuntimeError("The DOCX→PDF backend did not produce a PDF")
        validate_pdf(produced)
        inspect_pdf_quality(
            produced,
            expected_text=expected,
            min_recall=min_text_recall,
            expected_images=document.feature_count("Image"),
        )
        return publish_file(produced, destination, [source], validator=validate_pdf)

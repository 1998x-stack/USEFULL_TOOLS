"""Inspect actual OOXML output independently of Pandoc's source AST."""

import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass

from devkit.convert.ir import DocumentIR

_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
_A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"


@dataclass(frozen=True)
class DocxStructure:
    headings: int
    tables: int
    hyperlinks: int
    images: int
    paragraphs: int
    bold_runs: int
    italic_runs: int
    list_items: int


def inspect_docx(path) -> DocxStructure:
    """Count semantic OOXML elements; do not inspect source Markdown here."""
    with zipfile.ZipFile(path) as archive:
        document = ET.fromstring(archive.read("word/document.xml"))
        media_files = {
            name for name in archive.namelist()
            if name.startswith("word/media/") and not name.endswith("/")
        }
    paragraphs = document.findall(".//" + _W + "p")
    heading_count = 0
    list_count = 0
    for paragraph in paragraphs:
        style = paragraph.find("./" + _W + "pPr/" + _W + "pStyle")
        value = style.get(_W + "val", "") if style is not None else ""
        if value.lower().startswith("heading"):
            heading_count += 1
        if paragraph.find("./" + _W + "pPr/" + _W + "numPr") is not None or value == "ListParagraph":
            list_count += 1
    return DocxStructure(
        headings=heading_count,
        tables=len(document.findall(".//" + _W + "tbl")),
        hyperlinks=len(document.findall(".//" + _W + "hyperlink")),
        images=max(len(document.findall(".//" + _A + "blip")), len(media_files)),
        paragraphs=len(paragraphs),
        bold_runs=len(document.findall(".//" + _W + "rPr/" + _W + "b")),
        italic_runs=len(document.findall(".//" + _W + "rPr/" + _W + "i")),
        list_items=list_count,
    )


def verify_docx_structure(path, source: DocumentIR) -> DocxStructure:
    """Reject silent structural disappearance on supported Markdown nodes."""
    from devkit.convert._safe import validate_docx

    validate_docx(path)
    actual = inspect_docx(path)
    required = {
        "headings": source.feature_count("Header"),
        "tables": source.feature_count("Table"),
        "hyperlinks": source.feature_count("Link"),
        "images": source.feature_count("Image"),
    }
    for kind, count in required.items():
        if getattr(actual, kind) < count:
            raise ValueError(
                f"DOCX structure missing {kind}: expected at least {count}, found {getattr(actual, kind)}"
            )
    return actual

"""Create a CJK-aware reference DOCX using Pandoc's complete default styles.

Pandoc requires its own expected style IDs (in particular tables and lists).
A blank python-docx Document() is NOT a valid Pandoc reference: it can cause
tables to collapse into single-column text and unexpected page breaks.
"""

import shutil
import subprocess
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Mm, Pt

from devkit.convert.fonts import FontChoice


def _set_font(style, family: str, size=None):
    style.font.name = family
    if size is not None:
        style.font.size = Pt(size)
    props = style._element.get_or_add_rPr()
    fonts = props.rFonts
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        props.insert(0, fonts)
    for category in ("ascii", "hAnsi", "eastAsia", "cs"):
        fonts.set(qn("w:" + category), family)


def build_reference_docx(font: FontChoice, output: str) -> str:
    """Start with Pandoc's reference.docx and adjust its CJK typography.

    Keep all Pandoc-provided table/list/caption/first-paragraph styles.
    A minimal python-docx document lacks those style definitions.
    """
    executable = shutil.which("pandoc")
    if not executable:
        raise FileNotFoundError("Pandoc binary is required to create a DOCX reference style")
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with destination.open("wb") as out:
            result = subprocess.run(
                [executable, "--print-default-data-file", "reference.docx"],
                stdout=out, stderr=subprocess.PIPE, timeout=30, check=False,
            )
        if result.returncode != 0:
            detail = result.stderr.decode("utf-8", "replace")[-500:]
            raise RuntimeError(f"Unable to read Pandoc default DOCX template: {detail}")
        document = Document(str(destination))
        section = document.sections[0]
        section.page_width = Mm(210)
        section.page_height = Mm(297)
        section.left_margin = Mm(19)
        section.right_margin = Mm(19)
        section.top_margin = Mm(18)
        section.bottom_margin = Mm(18)

        styles = document.styles
        names = [
            "Normal", "Body Text", "First Paragraph", "Compact", "Caption",
            "Table Caption", "Quote", "Block Text", "List Paragraph", "List Bullet",
            "List Number", "Table", "Table Normal",
        ]
        names.extend("Heading " + str(level) for level in range(1, 7))
        for name in names:
            try:
                item = styles[name]
            except KeyError:
                continue
            _set_font(item, font.family, size=10.5 if name == "Normal" else None)
        document.save(str(destination))
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    return str(destination)

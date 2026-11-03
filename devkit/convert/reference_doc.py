"""Create a temporary Pandoc reference DOCX with explicit CJK styles."""

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
    """Provide Pandoc and LibreOffice with stable document and CJK font hints."""
    document = Document()
    section = document.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.left_margin = Mm(19)
    section.right_margin = Mm(19)
    section.top_margin = Mm(18)
    section.bottom_margin = Mm(18)

    styles = document.styles
    names = ["Normal", "Body Text", "Caption", "Quote", "List Paragraph",
             "List Bullet", "List Number", "Table Normal"]
    names.extend("Heading " + str(level) for level in range(1, 7))
    for name in names:
        try:
            item = styles[name]
        except KeyError:
            continue
        _set_font(item, font.family, size=10.5 if name == "Normal" else None)
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    document.save(output)
    return str(output)

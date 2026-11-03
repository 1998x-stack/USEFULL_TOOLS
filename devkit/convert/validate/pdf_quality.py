"""Read-back validation of Markdown-derived PDF text, graphics and page bounds."""

import unicodedata
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Optional, Tuple

import fitz


@dataclass(frozen=True)
class PDFQuality:
    pages: int
    expected_characters: int
    matched_characters: int
    text_recall: float
    image_instances: int
    clipped_characters: int
    replacement_glyphs: int
    blank_pages: Tuple[int, ...]
    pdf_fonts: Tuple[str, ...]

    def as_dict(self):
        return asdict(self)


def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    return "".join(ch for ch in normalized if not ch.isspace() and ch not in ("\u00ad", "\ufeff"))


def expected_text_from_ast(ast) -> str:
    """Collect visible text from Pandoc AST, excluding image alt text."""
    output = []

    def visit(node):
        if isinstance(node, list):
            for item in node:
                visit(item)
        elif isinstance(node, dict):
            tag = node.get("t")
            payload = node.get("c")
            if tag == "Image":
                return  # alt text need not be printed when the image is present
            if tag == "Str" and isinstance(payload, str):
                output.append(payload)
                return
            if tag in ("Code", "CodeBlock", "Math") and isinstance(payload, list):
                if isinstance(payload[-1], str):
                    output.append(payload[-1])
                return
            if tag in ("RawInline", "RawBlock"):
                return
            if "t" in node:
                visit(payload)
            else:
                for value in node.values():
                    visit(value)

    for block in ast["blocks"]:
        visit(block)
    return "".join(output)


def inspect_pdf_quality(
    path,
    *,
    expected_text: str = "",
    min_recall: float = 0.995,
    expected_images: int = 0,
    max_pages: int = 100,
) -> PDFQuality:
    """Inspect real Unicode extraction, char bboxes, raster and image presence.

    Not a full visual-equivalence proof. Off-page bounding boxes are a clipping
    signal; text fully omitted by a renderer is covered by text recall instead.
    """
    if not 0 <= min_recall <= 1:
        raise ValueError("min_recall must be between 0 and 1")
    with fitz.open(str(path)) as document:
        if not 1 <= document.page_count <= max_pages:
            raise ValueError(f"Invalid or excessive PDF page count: {document.page_count}")
        extracted = []
        clipped = 0
        replacement = 0
        blank = []
        images = 0
        fonts = set()
        for page_index, page in enumerate(document):
            extracted.append(page.get_text("text"))
            images += len(page.get_image_info())
            for detail in page.get_fonts(full=True):
                fonts.add(str(detail[3]))
            raw = page.get_text("rawdict")
            for block in raw["blocks"]:
                for line in block.get("lines", ()):
                    for span in line["spans"]:
                        for char in span["chars"]:
                            value = char["c"]
                            if value in ("\ufffd", "\u25a1", "\u25af"):
                                replacement += 1
                            rect = fitz.Rect(char["bbox"])
                            # Page boundaries should contain character boxes,
                            # allowing a small tolerance for glyph extents.
                            if (rect.x0 < -2 or rect.y0 < -2 or
                                    rect.x1 > page.rect.width + 2 or
                                    rect.y1 > page.rect.height + 2):
                                clipped += 1
            raster = page.get_pixmap(matrix=fitz.Matrix(0.7, 0.7), colorspace=fitz.csRGB, alpha=False)
            pixels = raster.samples
            if not any(byte < 244 for byte in pixels[::3]):
                blank.append(page_index + 1)
        expected = Counter(_normalize_text(expected_text))
        actual = Counter(_normalize_text("".join(extracted)))
        requested = sum(expected.values())
        matched = sum(min(count, actual[character]) for character, count in expected.items())
        recall = matched / requested if requested else 1.0
        result = PDFQuality(
            pages=document.page_count,
            expected_characters=requested,
            matched_characters=matched,
            text_recall=recall,
            image_instances=images,
            clipped_characters=clipped,
            replacement_glyphs=replacement,
            blank_pages=tuple(blank),
            pdf_fonts=tuple(sorted(fonts)),
        )
    if result.replacement_glyphs:
        raise ValueError(f"PDF contains {result.replacement_glyphs} missing/replacement glyph(s)")
    if result.clipped_characters:
        raise ValueError(f"PDF has {result.clipped_characters} off-page text character(s)")
    if result.text_recall + 1e-9 < min_recall:
        raise ValueError(
            f"PDF text recall {result.text_recall:.4f} below required {min_recall:.4f} "
            f"({matched}/{requested} characters)"
        )
    if result.image_instances < expected_images:
        raise ValueError(f"PDF image count {result.image_instances} below expected {expected_images}")
    if result.blank_pages and len(result.blank_pages) == result.pages and requested:
        raise ValueError("PDF raster has no visible content")
    return result

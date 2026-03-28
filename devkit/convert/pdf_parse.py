"""AI-powered PDF to Markdown parser."""

from typing import Optional


def pdf_to_markdown(
    input_path: str,
    output_dir: Optional[str] = None,
    model: str = "gpt-4o",
    api_key: Optional[str] = None,
) -> str:
    """Parse a PDF and convert to Markdown using AI vision.

    Requires: PyMuPDF, shapely (pip install devkit-tools[convert])
    """
    raise NotImplementedError(
        "PDF parsing requires AI API access. "
        "See devkit.convert.pdf_parse for the full implementation."
    )

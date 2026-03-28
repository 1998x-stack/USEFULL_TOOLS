"""Markdown to PDF converter."""

import os
from typing import Optional


def markdown_to_pdf(input_path: str, output_path: Optional[str] = None) -> str:
    try:
        import markdown2
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    except ImportError:
        raise ImportError("markdown2 and reportlab required: pip install devkit-tools[convert]")
    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + ".pdf"
    with open(input_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    html_content = markdown2.markdown(md_content)
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    content = []
    import re
    for para in re.split(r"\n\s*\n", html_content):
        clean = re.sub(r"<[^>]+>", "", para).strip()
        if clean:
            content.append(Paragraph(clean, styles["Normal"]))
            content.append(Spacer(1, 12))
    if content:
        doc.build(content)
    return output_path

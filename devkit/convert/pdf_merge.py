"""Merge multiple PDF files."""

import os


def merge_pdfs(input_dir: str, output_file: str) -> int:
    try:
        from PyPDF2 import PdfMerger
    except ImportError:
        raise ImportError("PyPDF2 is required: pip install devkit-tools[convert]")
    pdf_files = sorted(f for f in os.listdir(input_dir) if f.lower().endswith(".pdf"))
    if not pdf_files:
        return 0
    merger = PdfMerger()
    for pdf_file in pdf_files:
        merger.append(os.path.join(input_dir, pdf_file))
    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
    with open(output_file, "wb") as f:
        merger.write(f)
    merger.close()
    return len(pdf_files)

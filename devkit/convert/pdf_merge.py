"""Safely merge PDF files using maintained pypdf APIs."""

import os
import tempfile
from pathlib import Path

from devkit.convert._safe import publish_file, require_distinct, validate_pdf


def merge_pdfs(input_dir: str, output_file: str) -> int:
    """Merge eligible PDFs in lexical order, excluding an existing destination.

    Returns the number of source PDFs (not the page count); empty directories
    preserve the previous output and return zero.
    """
    try:
        from pypdf import PdfWriter
    except ImportError as exc:
        raise ImportError("pypdf is required: pip install -e '.[convert]'") from exc
    directory = Path(input_dir)
    if not directory.is_dir():
        raise NotADirectoryError(str(directory))
    candidates = []
    for path in sorted(directory.iterdir()):
        if path.suffix.lower() != ".pdf" or not path.is_file():
            continue
        if os.path.realpath(path) == os.path.realpath(output_file):
            continue
        if os.path.exists(output_file) and os.path.samefile(path, output_file):
            continue
        candidates.append(path)
    if not candidates:
        return 0
    require_distinct(candidates, output_file)

    writer = PdfWriter()
    try:
        for source in candidates:
            writer.append(str(source))
        with tempfile.TemporaryDirectory(prefix="devkit-merge-") as directory_tmp:
            staged = Path(directory_tmp) / "merged.pdf"
            writer.write(str(staged))
            validate_pdf(staged)
            publish_file(staged, output_file, candidates, validator=validate_pdf)
    finally:
        writer.close()
    return len(candidates)

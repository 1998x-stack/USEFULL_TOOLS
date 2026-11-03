"""Safely compress PDFs through Ghostscript with output validation."""

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from devkit.convert._safe import publish_file, require_distinct, validate_pdf

QUALITY_SETTINGS = {
    "screen": "/screen",
    "ebook": "/ebook",
    "printer": "/printer",
    "prepress": "/prepress",
}


def compress_pdf(input_path: str, output_path: Optional[str] = None, quality: str = "ebook") -> str:
    """Rewrite a PDF at the selected Ghostscript quality.

    This method may not reduce file size for every input. No output is published
    if conversion fails, or if the resulting page count differs.
    """
    binary = shutil.which("gs")
    if not binary:
        raise FileNotFoundError("Ghostscript (gs) is required but not found")
    if quality not in QUALITY_SETTINGS:
        raise ValueError(f"Unsupported quality: {quality}")
    source = Path(input_path).absolute()
    if not source.is_file():
        raise FileNotFoundError(str(source))
    destination = output_path or str(source.with_name(source.stem + "_compressed.pdf"))
    require_distinct([source], destination)
    source_pages = validate_pdf(source)
    with tempfile.TemporaryDirectory(prefix="devkit-gs-") as directory:
        produced = Path(directory) / "compressed.pdf"
        result = subprocess.run(
            [
                binary, "-dSAFER", "-sDEVICE=pdfwrite",
                "-dCompatibilityLevel=1.4",
                f"-dPDFSETTINGS={QUALITY_SETTINGS[quality]}",
                "-dNOPAUSE", "-dQUIET", "-dBATCH",
                f"-sOutputFile={produced}", str(source),
            ],
            capture_output=True, text=True, timeout=180, check=False,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "").strip()[-1500:]
            raise RuntimeError(f"Ghostscript failed (exit {result.returncode}): {detail}")
        if not produced.is_file() or validate_pdf(produced) != source_pages:
            raise ValueError("Compressed PDF is missing or has a different page count")
        return publish_file(produced, destination, [source], validator=validate_pdf)

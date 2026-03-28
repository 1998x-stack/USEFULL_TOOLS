"""Compress PDF files using Ghostscript."""

import os
import shutil
import subprocess
from typing import Optional

QUALITY_SETTINGS = {"screen": "/screen", "ebook": "/ebook", "printer": "/printer", "prepress": "/prepress"}


def compress_pdf(input_path: str, output_path: Optional[str] = None, quality: str = "ebook") -> Optional[str]:
    if not shutil.which("gs"):
        raise FileNotFoundError("Ghostscript (gs) is required but not found.")
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_compressed{ext}"
    setting = QUALITY_SETTINGS.get(quality, "/ebook")
    result = subprocess.run(
        ["gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
         f"-dPDFSETTINGS={setting}", "-dNOPAUSE", "-dQUIET", "-dBATCH",
         f"-sOutputFile={output_path}", input_path],
        capture_output=True,
    )
    if result.returncode == 0:
        return output_path
    return None

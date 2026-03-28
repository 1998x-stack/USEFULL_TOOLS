"""Document format conversion."""

import os
import shutil
import subprocess
from typing import Optional


def convert_document(input_path: str, to_format: str, output_path: Optional[str] = None) -> Optional[str]:
    if to_format == "pdf" and input_path.endswith((".docx", ".doc")):
        return _word_to_pdf(input_path, output_path)
    elif to_format == "md" and input_path.endswith((".docx", ".doc")):
        return _word_to_markdown(input_path, output_path)
    elif to_format == "docx" and input_path.endswith(".md"):
        return _markdown_to_word(input_path, output_path)
    return None


def _word_to_pdf(input_path, output_path=None):
    if not shutil.which("libreoffice"):
        raise FileNotFoundError("LibreOffice is required for Word->PDF conversion.")
    out_dir = os.path.dirname(output_path) if output_path else "."
    os.makedirs(out_dir, exist_ok=True)
    result = subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf", input_path, "--outdir", out_dir], capture_output=True)
    if result.returncode == 0:
        expected = os.path.join(out_dir, os.path.splitext(os.path.basename(input_path))[0] + ".pdf")
        return expected if os.path.exists(expected) else None
    return None


def _word_to_markdown(input_path, output_path=None):
    if not shutil.which("pandoc"):
        raise FileNotFoundError("Pandoc is required for Word->Markdown conversion.")
    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + ".md"
    result = subprocess.run(["pandoc", input_path, "-o", output_path], capture_output=True)
    return output_path if result.returncode == 0 else None


def _markdown_to_word(input_path, output_path=None):
    if not shutil.which("pandoc"):
        raise FileNotFoundError("Pandoc is required for Markdown->Word conversion.")
    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + ".docx"
    result = subprocess.run(["pandoc", input_path, "-o", output_path], capture_output=True)
    return output_path if result.returncode == 0 else None

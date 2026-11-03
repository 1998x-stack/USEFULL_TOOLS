"""Document conversion via isolated LibreOffice / Pandoc processes."""

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from devkit.convert._safe import publish_file, validate_docx, validate_pdf


def _executable(*candidates):
    for candidate in candidates:
        found = shutil.which(candidate)
        if found:
            return found
    raise FileNotFoundError(f"Required conversion tool not found: {' or '.join(candidates)}")


def _run(command, timeout=120):
    """Never use a shell; fail loudly on tool errors and timeouts."""
    completed = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()[-1500:]
        raise RuntimeError(f"Document conversion failed (exit {completed.returncode}): {detail}")


def convert_document(input_path: str, to_format: str, output_path: Optional[str] = None) -> Optional[str]:
    """Convert Word->PDF, Word->Markdown, or Markdown->DOCX.

    Unsupported pairs retain the previous None return convention.
    """
    ext = Path(input_path).suffix.lower()
    if ext in (".docx", ".doc") and to_format == "pdf":
        return _word_to_pdf(input_path, output_path)
    if ext in (".docx", ".doc") and to_format == "md":
        return _word_to_markdown(input_path, output_path)
    if ext == ".md" and to_format == "docx":
        return _markdown_to_word(input_path, output_path)
    return None


def _word_to_pdf(input_path: str, output_path: Optional[str] = None) -> str:
    binary = _executable("libreoffice", "soffice")
    source = Path(input_path).absolute()
    if not source.is_file():
        raise FileNotFoundError(str(source))
    destination = output_path or str(source.with_suffix(".pdf"))
    with tempfile.TemporaryDirectory(prefix="devkit-lo-") as directory:
        workdir = Path(directory)
        output_dir = workdir / "converted"
        output_dir.mkdir()
        profile = workdir / "profile"
        _run([
            binary,
            "-env:UserInstallation=" + profile.as_uri(),
            "--headless",
            "--convert-to", "pdf:writer_pdf_Export",
            "--outdir", str(output_dir),
            str(source),
        ])
        produced = output_dir / (source.stem + ".pdf")
        if not produced.is_file():
            raise RuntimeError(f"LibreOffice did not produce expected PDF: {produced}")
        return publish_file(produced, destination, [source], validator=validate_pdf)


def _word_to_markdown(input_path: str, output_path: Optional[str] = None) -> str:
    binary = _executable("pandoc")
    source = Path(input_path).absolute()
    if not source.is_file():
        raise FileNotFoundError(str(source))
    destination = output_path or str(source.with_suffix(".md"))
    with tempfile.TemporaryDirectory(prefix="devkit-pandoc-") as directory:
        produced = Path(directory) / "output.md"
        _run([binary, str(source), "-t", "gfm", "-o", str(produced)])
        if not produced.is_file():
            raise RuntimeError("Pandoc did not produce Markdown")
        return publish_file(produced, destination, [source])


def _markdown_to_word(input_path: str, output_path: Optional[str] = None) -> str:
    binary = _executable("pandoc")
    source = Path(input_path).absolute()
    if not source.is_file():
        raise FileNotFoundError(str(source))
    destination = output_path or str(source.with_suffix(".docx"))
    with tempfile.TemporaryDirectory(prefix="devkit-pandoc-") as directory:
        produced = Path(directory) / "output.docx"
        _run([binary, str(source), "-f", "gfm", "-o", str(produced)])
        if not produced.is_file():
            raise RuntimeError("Pandoc did not produce DOCX")
        return publish_file(produced, destination, [source], validator=validate_docx)

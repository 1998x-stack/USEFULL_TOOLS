"""Shared safe publication and format checks for document conversion."""

import os
import shutil
import tempfile
import zipfile
from pathlib import Path


def require_distinct(input_paths, output_path):
    """Reject in-place conversion and destination aliases, including hard links."""
    destination = Path(output_path)
    if destination.is_symlink():
        raise ValueError(f"Refusing symlink destination: {destination}")
    for source in input_paths:
        source = Path(source)
        if os.path.realpath(source) == os.path.realpath(destination):
            raise ValueError(f"Output must differ from input: {destination}")
        if source.exists() and destination.exists() and os.path.samefile(source, destination):
            raise ValueError(f"Output is a hard-link alias of input: {destination}")


def validate_pdf(path):
    """Require at least one parseable PDF page."""
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ImportError("pypdf is required: pip install -e '.[convert]'") from exc
    reader = PdfReader(str(path), strict=True)
    if reader.is_encrypted:
        raise ValueError("Unexpected encrypted PDF output")
    count = len(reader.pages)
    if count < 1:
        raise ValueError(f"Generated PDF contains no pages: {path}")
    return count


def validate_docx(path):
    """Verify ZIP integrity and the required Word document part."""
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError(f"Corrupt DOCX ZIP: {path}")
        if "word/document.xml" not in archive.namelist():
            raise ValueError(f"Missing DOCX document part: {path}")


def publish_file(source_path, output_path, input_paths=(), validator=None):
    """Copy to a sibling temporary file and replace only after validation.

    This is single-file atomic publication on the same filesystem; it is not
    a cross-process transaction or a crash-safe multi-file commit.
    """
    require_distinct(input_paths, output_path)
    if validator is not None:
        validator(source_path)
    destination = Path(output_path).absolute()
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".devkit-convert-", dir=str(destination.parent))
    try:
        with os.fdopen(fd, "wb") as out, open(source_path, "rb") as src:
            shutil.copyfileobj(src, out, 1024 * 1024)
            out.flush()
            os.fsync(out.fileno())
        if validator is not None:
            validator(temporary)
        require_distinct(input_paths, destination)
        os.replace(temporary, destination)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return str(output_path)

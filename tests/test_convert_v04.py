"""V0.4 conversion safety and output-contract regression tests."""

import os
import subprocess
import zipfile
from pathlib import Path
from types import SimpleNamespace

import pytest
from pypdf import PdfReader, PdfWriter

from devkit.convert import doc_convert
from devkit.convert._safe import publish_file, require_distinct, validate_docx, validate_pdf
from devkit.convert.pdf_compress import compress_pdf
from devkit.convert.pdf_merge import merge_pdfs


def _pdf(path, pages=1):
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=595, height=842)
    writer.write(str(path))
    writer.close()


def test_pdf_merge_preserves_page_order_and_excludes_existing_output(tmp_path):
    _pdf(tmp_path / "01.pdf", 1)
    _pdf(tmp_path / "02.pdf", 2)
    out = tmp_path / "combined.pdf"
    _pdf(out, 6)
    assert merge_pdfs(str(tmp_path), str(out)) == 2
    assert len(PdfReader(str(out)).pages) == 3
    assert merge_pdfs(str(tmp_path), str(out)) == 2
    assert len(PdfReader(str(out)).pages) == 3


def test_pdf_merge_corrupt_input_preserves_existing_output(tmp_path):
    _pdf(tmp_path / "a.pdf")
    (tmp_path / "b.pdf").write_text("not a PDF")
    out = tmp_path / "merged.pdf"
    _pdf(out, 4)
    with pytest.raises(Exception):
        merge_pdfs(str(tmp_path), str(out))
    assert validate_pdf(out) == 4


def test_pdf_merge_empty_does_not_replace_output(tmp_path):
    out = tmp_path / "merged.pdf"
    out.write_bytes(b"KEEP")
    assert merge_pdfs(str(tmp_path), str(out)) == 0
    assert out.read_bytes() == b"KEEP"


def test_reject_samefile_and_symlink_output(tmp_path):
    source = tmp_path / "input.pdf"
    _pdf(source)
    with pytest.raises(ValueError, match="must differ"):
        require_distinct([source], source)
    link = tmp_path / "alias.pdf"
    try:
        os.symlink(source, link)
    except (NotImplementedError, OSError):
        pytest.skip("symlinks unsupported")
    with pytest.raises(ValueError, match="symlink"):
        require_distinct([source], link)


def test_publish_file_validation_failure_is_atomic(tmp_path):
    source = tmp_path / "invalid.pdf"
    source.write_bytes(b"invalid PDF")
    target = tmp_path / "output.pdf"
    _pdf(target, 2)
    with pytest.raises(Exception):
        publish_file(source, target, validator=validate_pdf)
    assert validate_pdf(target) == 2
    assert not list(tmp_path.glob(".devkit-convert-*"))


def test_pdf_compress_rejects_in_place_before_subprocess(tmp_path, monkeypatch):
    source = tmp_path / "source.pdf"
    _pdf(source)
    monkeypatch.setattr("devkit.convert.pdf_compress.shutil.which", lambda _: "gs")
    with pytest.raises(ValueError, match="must differ"):
        compress_pdf(str(source), output_path=str(source))
    assert validate_pdf(source) == 1


def test_pdf_compress_failure_does_not_replace_output(tmp_path, monkeypatch):
    source = tmp_path / "source.pdf"
    target = tmp_path / "output.pdf"
    _pdf(source)
    _pdf(target, 3)
    monkeypatch.setattr("devkit.convert.pdf_compress.shutil.which", lambda _: "gs")
    monkeypatch.setattr(
        "devkit.convert.pdf_compress.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(returncode=1, stdout="", stderr="bad PDF"),
    )
    with pytest.raises(RuntimeError, match="Ghostscript failed"):
        compress_pdf(str(source), output_path=str(target))
    assert validate_pdf(target) == 3


def test_pdf_compress_missing_output_is_not_success(tmp_path, monkeypatch):
    source = tmp_path / "source.pdf"
    _pdf(source)
    monkeypatch.setattr("devkit.convert.pdf_compress.shutil.which", lambda _: "gs")
    monkeypatch.setattr(
        "devkit.convert.pdf_compress.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="", stderr=""),
    )
    with pytest.raises(ValueError, match="missing"):
        compress_pdf(str(source), output_path=str(tmp_path / "result.pdf"))
    assert not (tmp_path / "result.pdf").exists()


def test_pdf_compress_invalid_quality(tmp_path, monkeypatch):
    monkeypatch.setattr("devkit.convert.pdf_compress.shutil.which", lambda _: "gs")
    with pytest.raises(ValueError, match="quality"):
        compress_pdf(str(tmp_path / "source.pdf"), quality="other")


def test_word_to_pdf_honors_explicit_custom_path(tmp_path, monkeypatch):
    original = tmp_path / "original.docx"
    original.write_bytes(b"mock input for isolated runner")
    target = tmp_path / "custom" / "renamed-result.pdf"
    monkeypatch.setattr(doc_convert, "_executable", lambda *args: "fake-soffice")

    def mock_run(command, timeout=120):
        assert "-env:UserInstallation=" in " ".join(command)
        outdir = Path(command[command.index("--outdir") + 1])
        _pdf(outdir / "original.pdf", 2)

    monkeypatch.setattr(doc_convert, "_run", mock_run)
    result = doc_convert.convert_document(str(original), "pdf", str(target))
    assert result == str(target)
    assert validate_pdf(target) == 2
    assert original.read_bytes() == b"mock input for isolated runner"


def test_word_to_pdf_no_file_keeps_old_output(tmp_path, monkeypatch):
    source = tmp_path / "source.docx"
    source.write_bytes(b"mock")
    out = tmp_path / "existing.pdf"
    _pdf(out, 3)
    monkeypatch.setattr(doc_convert, "_executable", lambda *args: "fake-soffice")
    monkeypatch.setattr(doc_convert, "_run", lambda command, timeout=120: None)
    with pytest.raises(RuntimeError, match="did not produce"):
        doc_convert.convert_document(str(source), "pdf", str(out))
    assert validate_pdf(out) == 3


def test_doc_to_markdown_honors_custom_destination(tmp_path, monkeypatch):
    source = tmp_path / "source.docx"
    source.write_bytes(b"mock")
    target = tmp_path / "custom" / "notes.md"
    monkeypatch.setattr(doc_convert, "_executable", lambda *args: "pandoc")

    def mock_run(command, timeout=120):
        output = Path(command[command.index("-o") + 1])
        output.write_text("# Heading\n\nBody", encoding="utf-8")

    monkeypatch.setattr(doc_convert, "_run", mock_run)
    assert doc_convert.convert_document(str(source), "md", str(target)) == str(target)
    assert target.read_text(encoding="utf-8") == "# Heading\n\nBody"


def test_markdown_to_docx_requires_real_document_part(tmp_path, monkeypatch):
    source = tmp_path / "source.md"
    source.write_text("# Demo", encoding="utf-8")
    target = tmp_path / "converted.docx"
    monkeypatch.setattr(doc_convert, "_executable", lambda *args: "pandoc")

    def mock_run(command, timeout=120):
        with zipfile.ZipFile(command[-1], "w") as archive:
            archive.writestr("other.txt", "invalid")

    monkeypatch.setattr(doc_convert, "_run", mock_run)
    with pytest.raises(ValueError, match="Missing DOCX"):
        doc_convert.convert_document(str(source), "docx", str(target))
    assert not target.exists()


def test_unrelated_conversion_retains_none(tmp_path):
    assert doc_convert.convert_document(str(tmp_path / "input.pdf"), "docx") is None


def test_subprocess_timeout_is_bounded(monkeypatch):
    def mock_run(command, **kwargs):
        assert kwargs["timeout"] == 120
        raise subprocess.TimeoutExpired(command, 120)

    monkeypatch.setattr(doc_convert.subprocess, "run", mock_run)
    with pytest.raises(subprocess.TimeoutExpired):
        doc_convert._run(["pandoc", "example.md"])


def test_validate_docx_rejects_plain_zip(tmp_path):
    path = tmp_path / "invalid.docx"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("arbitrary.txt", "abc")
    with pytest.raises(ValueError, match="Missing DOCX"):
        validate_docx(path)

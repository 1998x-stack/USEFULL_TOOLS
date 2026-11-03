"""V0.4-E quality policies, report contracts, CLI, and real rendering regression."""

import json
import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner

from devkit.cli import cli
from devkit.convert.quality import (
    PROFILES,
    ConversionFailure,
    audit_existing,
    convert_with_quality,
)


@pytest.fixture
def simple_md(tmp_path):
    source = tmp_path / "article.md"
    source.write_text(
        "# 中文 Alpha\n\nA **bold** word and *italic* phrase.\n\n"
        "## Data\n\n| Name | Value |\n|---|---|\n| Alpha | 95 |\n",
        encoding="utf-8",
    )
    return source


def test_named_profile_contracts():
    assert set(PROFILES) == {"fast", "standard", "strict"}
    assert not PROFILES["fast"].audit_structure
    assert PROFILES["standard"].audit_structure
    assert PROFILES["strict"].requires_visual_pdf
    assert PROFILES["strict"].min_text_recall >= PROFILES["standard"].min_text_recall


def test_unknown_profile_rejected(simple_md):
    with pytest.raises(ValueError, match="Unknown quality profile"):
        convert_with_quality(simple_md, "docx", profile="nope")


def test_fast_docx_publishes_report_and_preserves_input(simple_md, tmp_path):
    if not shutil.which("pandoc"):
        pytest.skip("pandoc required")
    out, report = tmp_path / "final.docx", tmp_path / "report" / "quality.json"
    before = simple_md.read_bytes()
    result = convert_with_quality(simple_md, "docx", out, profile="fast", report_path=report)
    assert result.output_path == str(out)
    assert result.report.status == "passed"
    assert result.report.achieved_level == "L1"
    assert simple_md.read_bytes() == before
    record = json.loads(report.read_text(encoding="utf-8"))
    assert record["schema_version"] == 1
    assert record["status"] == "passed"
    assert record["checks"][-1]["name"] == "atomic_output_published"
    assert record["elapsed_ms"] >= 0


def test_standard_docx_independent_structure_report(simple_md, tmp_path):
    if not shutil.which("pandoc"):
        pytest.skip("pandoc required")
    result = convert_with_quality(simple_md, "docx", tmp_path / "out.docx")
    assert result.report.achieved_level == "L2"
    assert result.report.metrics["docx"]["headings"] >= 2
    assert result.report.metrics["docx"]["tables"] == 1
    assert any(check["name"] == "docx_structural_counts" for check in result.report.checks)


def test_strict_docx_text_and_styles(simple_md, tmp_path):
    if not shutil.which("pandoc"):
        pytest.skip("pandoc required")
    result = convert_with_quality(simple_md, "docx", tmp_path / "out.docx", profile="strict")
    assert result.report.achieved_level == "L2"
    assert result.report.metrics["docx_text_recall"] >= 0.999
    assert any(check["name"] == "docx_strict_formatting_and_text" for check in result.report.checks)


def test_failed_image_preserves_old_output_and_writes_report(tmp_path):
    if not shutil.which("pandoc"):
        pytest.skip("pandoc required")
    source = tmp_path / "bad.md"
    source.write_text("# Broken\n\n![missing](assets/not-here.png)", encoding="utf-8")
    out = tmp_path / "out.docx"
    out.write_bytes(b"KEEP THE ORIGINAL")
    report = tmp_path / "failure.json"
    with pytest.raises(ConversionFailure):
        convert_with_quality(source, "docx", out, report_path=report)
    assert out.read_bytes() == b"KEEP THE ORIGINAL"
    record = json.loads(report.read_text())
    assert record["status"] == "failed"
    assert record["diagnostics"][0]["severity"] == "error"
    assert all(check["name"] != "atomic_output_published" for check in record["checks"])


def test_strict_pdf_requires_visual_evidence_before_render(simple_md, tmp_path):
    out = tmp_path / "existing.pdf"
    out.write_bytes(b"OLD")
    report = tmp_path / "failed.json"
    with pytest.raises(ConversionFailure, match="Strict PDF requires"):
        convert_with_quality(simple_md, "pdf", out, profile="strict", report_path=report)
    assert out.read_bytes() == b"OLD"
    assert json.loads(report.read_text())["status"] == "failed"


def test_recall_override_cannot_weaken_profile(simple_md, tmp_path):
    report = tmp_path / "invalid.json"
    with pytest.raises(ConversionFailure, match="min_text_recall must be"):
        convert_with_quality(simple_md, "pdf", tmp_path / "out.pdf",
                             min_text_recall=0.2, report_path=report)
    assert not (tmp_path / "out.pdf").exists()
    assert json.loads(report.read_text())["status"] == "failed"


def test_report_source_alias_rejected(simple_md):
    original = simple_md.read_bytes()
    with pytest.raises(ValueError, match="must differ"):
        convert_with_quality(simple_md, "docx", report_path=simple_md)
    assert simple_md.read_bytes() == original


def test_report_output_alias_rejected(simple_md, tmp_path):
    output = tmp_path / "out.docx"
    output.write_bytes(b"KEEP")
    with pytest.raises(ValueError, match="must differ"):
        convert_with_quality(simple_md, "docx", output, report_path=output)
    assert output.read_bytes() == b"KEEP"


def test_strict_word_pdf_does_not_claim_visual_fidelity(tmp_path):
    source, report = tmp_path / "source.docx", tmp_path / "unsupported.json"
    source.write_bytes(b"mock")
    with pytest.raises(ConversionFailure, match="Strict profile is unsupported"):
        convert_with_quality(source, "pdf", profile="strict", report_path=report)
    assert json.loads(report.read_text())["status"] == "failed"


def test_source_output_alias_protection(simple_md):
    before = simple_md.read_bytes()
    with pytest.raises(ConversionFailure, match="must differ"):
        convert_with_quality(simple_md, "docx", simple_md)
    assert simple_md.read_bytes() == before


def test_existing_docx_audit_is_read_only(simple_md, tmp_path):
    if not shutil.which("pandoc"):
        pytest.skip("pandoc required")
    out = tmp_path / "document.docx"
    convert_with_quality(simple_md, "docx", out)
    before = out.read_bytes()
    report = audit_existing(simple_md, out, report_path=tmp_path / "audit.json")
    assert report.status == "passed" and report.achieved_level == "L2"
    assert out.read_bytes() == before
    assert any(c["name"] == "existing_output_assessed_without_modification" for c in report.checks)


def test_missing_existing_output_has_failed_report(simple_md, tmp_path):
    report = tmp_path / "failed.json"
    with pytest.raises(ConversionFailure, match="missing"):
        audit_existing(simple_md, tmp_path / "missing.docx", report_path=report)
    assert json.loads(report.read_text())["status"] == "failed"


def test_cli_docx_profile_and_report(simple_md, tmp_path):
    if not shutil.which("pandoc"):
        pytest.skip("pandoc required")
    out, report = tmp_path / "cli.docx", tmp_path / "quality.json"
    result = CliRunner().invoke(
        cli, ["convert", "md2docx", str(simple_md), "--profile", "standard",
              "--report", str(report), "-o", str(out)],
    )
    assert result.exit_code == 0, result.output
    assert "Quality: L2 / standard" in result.output
    assert out.exists() and report.exists()


def test_cli_audit_existing_is_read_only(simple_md, tmp_path):
    if not shutil.which("pandoc"):
        pytest.skip("pandoc required")
    out = tmp_path / "doc.docx"
    convert_with_quality(simple_md, "docx", out)
    before = out.read_bytes()
    result = CliRunner().invoke(cli, ["convert", "audit", str(simple_md), str(out), "--profile", "fast"])
    assert result.exit_code == 0, result.output
    assert "Audit passed: L1 / fast" in result.output
    assert out.read_bytes() == before


def test_cli_strict_failure_and_json_report(simple_md, tmp_path):
    report = tmp_path / "error.json"
    result = CliRunner().invoke(
        cli, ["convert", "md2pdf", str(simple_md), "--profile", "strict",
              "--report", str(report), "-o", str(tmp_path / "out.pdf")],
    )
    assert result.exit_code != 0
    assert "Strict PDF requires" in result.output
    assert json.loads(report.read_text())["status"] == "failed"


def test_audit_unsupported_format(tmp_path):
    src, out = tmp_path / "data.csv", tmp_path / "data.pdf"
    src.write_text("x,y\n1,2")
    with pytest.raises(ValueError, match="Unsupported conversion pair"):
        audit_existing(src, out)


def test_v03_data_cli_is_preserved():
    result = CliRunner().invoke(cli, ["data", "--help"])
    assert result.exit_code == 0
    assert "csv-merge" in result.output and "json-merge" in result.output


@pytest.mark.pdf_integration
def test_real_standard_pdf_quality_report(simple_md, tmp_path):
    if not all(shutil.which(cmd) for cmd in ("pandoc", "libreoffice", "fc-match")):
        pytest.skip("PDF backends missing")
    result = convert_with_quality(
        simple_md, "pdf", tmp_path / "out.pdf",
        report_path=tmp_path / "quality.json",
    )
    assert result.report.achieved_level == "L2"
    assert result.report.metrics["pdf"]["text_recall"] >= 0.995
    assert result.report.metrics["pdf"]["pages"] >= 1


@pytest.mark.visual_integration
def test_real_strict_pdf_with_approved_visual_evidence(tmp_path):
    root = Path(__file__).parent / "fixtures" / "visual_v04d"
    result = convert_with_quality(
        root / "cjk-layout.md", "pdf", tmp_path / "strict.pdf", profile="strict",
        visual_manifest=root / "manifest.json", visual_case="cjk-layout",
        artifacts_dir=tmp_path / "evidence", report_path=tmp_path / "report.json",
    )
    assert result.report.status == "passed"
    assert result.report.achieved_level == "L3"
    assert result.report.metrics["visual"]["status"] == "pass"
    assert (tmp_path / "evidence" / "cjk-layout-p01-diff.png").exists()


@pytest.mark.visual_integration
def test_strict_pdf_wrong_approved_source_never_publishes(tmp_path):
    root = Path(__file__).parent / "fixtures" / "visual_v04d"
    out = tmp_path / "existing.pdf"
    out.write_bytes(b"KEEP")
    with pytest.raises(ConversionFailure, match="must match identical approved Markdown"):
        convert_with_quality(
            root / "pagination.md", "pdf", out, profile="strict",
            visual_manifest=root / "manifest.json", visual_case="cjk-layout",
            artifacts_dir=tmp_path / "evidence",
        )
    assert out.read_bytes() == b"KEEP"

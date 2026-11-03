"""Independent PDF visual regressions; no baseline can self-approve."""

import hashlib
import json
from pathlib import Path

import fitz
import pytest
from PIL import Image, ImageDraw

from devkit.convert.visual import (
    _clip_rect,
    compare_images,
    compare_page,
    evaluate_pages,
    inspect_line_overlaps,
    load_manifest,
    render_pages,
    save_report,
)
from devkit.convert.visual_cli import main, run_suite


def _image(shift=0):
    image = Image.new("RGB", (180, 220), "white")
    pen = ImageDraw.Draw(image)
    pen.rectangle((22 + shift, 40, 140 + shift, 70), fill="black")
    pen.line((22, 100, 156, 100), fill="black", width=3)
    return image


def _settings():
    return {
        "dpi": 96, "max_pages": 8, "pixel_threshold": 28,
        "max_changed_fraction": 0.001, "max_mean_error": 0.3,
    }


def _pdf(path, *, shifted=False, two_pages=False):
    document = fitz.open()
    page = document.new_page(width=250, height=300)
    page.insert_text((40, 50 + (15 if shifted else 0)), "Golden 123", fontsize=18)
    if two_pages:
        document.new_page(width=250, height=300)
    document.save(str(path))
    document.close()


def _approved(tmp_path):
    approved = tmp_path / "approved"
    approved.mkdir()
    sample = _image()
    golden = approved / "sample-p01.png"
    sample.save(golden, optimize=True)
    case = {
        "id": "sample", "expected_pages": 1,
        "sha256": [hashlib.sha256(golden.read_bytes()).hexdigest()],
        "regions": [
            {"name": "table", "page": 1, "rect": [0.08, 0.14, 0.91, 0.37],
             "max_changed_fraction": 0.001},
        ],
    }
    manifest = {"schema_version": 1, "render": _settings(), "cases": [case]}
    return approved, case, manifest


def test_exact_equal_images_pass():
    ratio, error, passed, overlay = compare_images(_image(), _image())
    assert ratio == 0
    assert error == 0
    assert passed
    assert overlay.size == (180, 220)


def test_moved_heading_fails_pixel_gate():
    ratio, error, passed, _ = compare_images(
        _image(), _image(shift=12), max_fraction=0.005, max_mean_error=0.4
    )
    assert ratio > 0.005
    assert error > 0.4
    assert not passed


def test_region_specific_gate_catches_small_table_shift():
    baseline = _image()
    variant = _image()
    ImageDraw.Draw(variant).rectangle((32, 50, 52, 60), fill="white")
    config = dict(_settings())
    config["max_changed_fraction"] = 0.06
    config["max_mean_error"] = 12
    page, _ = compare_page(
        baseline, variant, 1, config,
        [{"page": 1, "name": "critical-table", "rect": [0.1, 0.16, 0.35, 0.30],
          "max_changed_fraction": 0.005, "max_mean_error": 0.4}],
    )
    assert page.changed_fraction < 0.06
    assert not page.passed
    assert not page.regions[0].passed


def test_region_geometry_validation():
    with pytest.raises(ValueError, match="normalized region"):
        _clip_rect({"rect": [-0.1, 0.2, 0.5, 0.5]}, (200, 100))
    with pytest.raises(ValueError, match="numeric"):
        _clip_rect({"rect": [0, "bad", 0.5, 0.5]}, (200, 100))


def test_mismatched_page_dimensions_are_error():
    with pytest.raises(ValueError, match="dimensions"):
        compare_images(_image(), Image.new("RGB", (181, 220), "white"))


def test_bad_thresholds_are_error():
    with pytest.raises(ValueError, match="pixel_threshold"):
        compare_images(_image(), _image(), pixel_threshold=0)
    with pytest.raises(ValueError, match="thresholds"):
        compare_images(_image(), _image(), max_fraction=1.2)


def test_approved_png_passes_and_outputs_artifacts(tmp_path):
    approved, case, manifest = _approved(tmp_path)
    result = evaluate_pages(case, [_image()], manifest, approved, tmp_path)
    assert result["status"] == "pass"
    assert result["pages"][0]["changed_fraction"] == 0
    assert (tmp_path / "sample-p01-actual.png").exists()
    assert (tmp_path / "sample-p01-diff.png").exists()


def test_approved_png_changes_require_new_hash_approval(tmp_path):
    approved, case, manifest = _approved(tmp_path)
    Image.new("RGB", (180, 220), "green").save(approved / "sample-p01.png")
    with pytest.raises(ValueError, match="without approval"):
        evaluate_pages(case, [_image()], manifest, approved, tmp_path)


def test_missing_png_is_not_created_during_verify(tmp_path):
    approved, case, manifest = _approved(tmp_path)
    (approved / "sample-p01.png").unlink()
    with pytest.raises(FileNotFoundError, match="golden PNG missing"):
        evaluate_pages(case, [_image()], manifest, approved, tmp_path)
    assert list(approved.iterdir()) == []


def test_pagination_regression_is_immediate_failure(tmp_path):
    approved, case, manifest = _approved(tmp_path)
    with pytest.raises(ValueError, match="pagination regression"):
        evaluate_pages(case, [_image(), _image()], manifest, approved, tmp_path)


def test_actual_visual_change_creates_red_highlight_diff(tmp_path):
    approved, case, manifest = _approved(tmp_path)
    result = evaluate_pages(case, [_image(shift=12)], manifest, approved, tmp_path)
    assert result["status"] == "fail"
    with Image.open(tmp_path / "sample-p01-diff.png") as diff:
        assert diff.getpixel((22, 40)) == (245, 45, 48) or diff.getpixel((140, 40)) == (245, 45, 48)


def test_invalid_manifest_rejected(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps({"schema_version": 8, "cases": []}))
    with pytest.raises(ValueError, match="schema"):
        load_manifest(path)
    path.write_text(json.dumps({
        "schema_version": 1, "render": _settings(),
        "cases": [{"id": "same"}, {"id": "same"}],
    }))
    with pytest.raises(ValueError, match="Duplicate"):
        load_manifest(path)


def test_html_json_report_escapes_untrusted_errors(tmp_path):
    save_report({
        "status": "fail", "cases": [
            {"id": "bad", "status": "fail", "error": "<script>bad()</script>"}
        ],
    }, tmp_path)
    text = (tmp_path / "report.html").read_text(encoding="utf-8")
    assert "<script>" not in text
    assert "&lt;script&gt;" in text
    parsed = json.loads((tmp_path / "report.json").read_text())
    assert parsed["status"] == "fail"


def test_pdf_raster_is_deterministic(tmp_path):
    pdf = tmp_path / "basic.pdf"
    _pdf(pdf)
    first = render_pages(pdf)
    second = render_pages(pdf)
    assert len(first) == 1
    assert first[0].tobytes() == second[0].tobytes()


def test_pdf_page_count_limit(tmp_path):
    pdf = tmp_path / "many.pdf"
    _pdf(pdf, two_pages=True)
    with pytest.raises(ValueError, match="page count"):
        render_pages(pdf, max_pages=1)


def test_line_overlap_reports_large_real_collision(tmp_path):
    pdf = tmp_path / "collision.pdf"
    doc = fitz.open()
    page = doc.new_page(width=280, height=280)
    page.insert_text((30, 60), "WIDE HEADER", fontsize=20)
    page.insert_text((31, 61), "WIDE HEADER", fontsize=20)
    doc.save(pdf)
    doc.close()
    assert inspect_line_overlaps(pdf)


def test_nonoverlapping_line_positions_pass(tmp_path):
    pdf = tmp_path / "clean.pdf"
    doc = fitz.open()
    page = doc.new_page(width=280, height=280)
    page.insert_text((30, 50), "First line", fontsize=12)
    page.insert_text((30, 90), "Second line", fontsize=12)
    doc.save(pdf)
    doc.close()
    assert not inspect_line_overlaps(pdf)


def test_cannot_emit_approved_baselines_from_verify():
    with pytest.raises(SystemExit) as exc:
        main(["verify", "--manifest", "unused.json", "--out-dir", "unused", "--emit-base64"])
    assert exc.value.code == 2


@pytest.mark.visual_integration
def test_real_approved_visual_goldens(tmp_path):
    manifest = Path(__file__).parent / "fixtures" / "visual_v04d" / "manifest.json"
    result = run_suite(manifest, tmp_path, "verify")
    assert result["status"] == "pass", result
    assert len(result["cases"]) == 2
    assert (tmp_path / "report.json").is_file()
    assert (tmp_path / "report.html").is_file()

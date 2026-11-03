"""V0.4-C CJK PDF conversion: independent checks plus real renderer coverage."""

import json
import shutil
from pathlib import Path

import fitz
import pytest
from click.testing import CliRunner
from PIL import Image

from devkit.cli import cli
from devkit.convert import fonts
from devkit.convert.md2pdf import markdown_to_pdf
from devkit.convert.validate.pdf_quality import expected_text_from_ast, inspect_pdf_quality


@pytest.fixture
def cjk_markdown(tmp_path):
    source = tmp_path / "cjk.md"
    source.write_text(
        "# 中文版式测试\n\n"
        "这里包含中文和日本語，English text remains selectable.\n\n"
        "## 实验数据\n\n"
        "| 名称 | 结果 |\n"
        "|---|---|\n"
        "| 样例A | 成功 |\n"
        "| 样例B | 稳定 |\n\n"
        "![插图](assets/chart.png)\n",
        encoding="utf-8",
    )
    folder = tmp_path / "assets"
    folder.mkdir()
    picture = Image.new("RGB", (50, 32), (200, 20, 70))
    picture.save(folder / "chart.png")
    return source


def _font_match(family):
    return (family, "/mock/noto.ttc", 0)


def test_cjk_detection_includes_han_kana_hangul():
    assert all(fonts.is_cjk(char) for char in "中文日本語한글")
    assert not fonts.is_cjk("A")


def test_choose_font_no_cjk_does_not_require_fontconfig(monkeypatch):
    monkeypatch.setattr(fonts.shutil, "which", lambda _: None)
    assert fonts.choose_cjk_font("English only 123") is None


def test_font_discovery_tries_fallback_and_checks_actual_cmap(monkeypatch):
    monkeypatch.setattr(fonts.shutil, "which", lambda _: "/usr/bin/fc-match")
    monkeypatch.setattr(fonts, "_fontconfig_match", _font_match)
    def codepoints(path, index):
        # The preferred SC font is mocked as lacking Kana; JP fallback has both.
        return {ord(x) for x in "中文"} if index == 0 else set()
    monkeypatch.setattr(fonts, "_font_characters", lambda path, index:
                        {ord(x) for x in "中文日本語"} if path.endswith("ttc") else codepoints(path, index))
    chosen = fonts.choose_cjk_font("中文日本語", preferred_family="Noto Sans CJK SC")
    assert chosen is not None
    assert chosen.coverage_checked == len(set("中文日本語"))


def test_font_discovery_rejects_partial_cmap(monkeypatch):
    monkeypatch.setattr(fonts.shutil, "which", lambda _: "/usr/bin/fc-match")
    monkeypatch.setattr(fonts, "_fontconfig_match", _font_match)
    monkeypatch.setattr(fonts, "_font_characters", lambda path, index: {ord("中")})
    with pytest.raises(ValueError, match="glyph coverage"):
        fonts.choose_cjk_font("中文日本語", preferred_family="Noto Sans CJK SC")


def test_expected_text_ignores_image_alt():
    ast = {"pandoc-api-version": [1, 23, 1], "meta": {}, "blocks": [
        {"t": "Para", "c": [
            {"t": "Str", "c": "中文"},
            {"t": "Space"},
            {"t": "Strong", "c": [{"t": "Str", "c": "bold"}]},
            {"t": "Image", "c": [["", [], []],
                                  [{"t": "Str", "c": "ALTTEXT"}],
                                  ["assets/plot.png", ""]]},
        ]},
    ]}
    expected = expected_text_from_ast(ast)
    assert "中文" in expected
    assert "bold" in expected
    assert "ALTTEXT" not in expected


def _text_pdf(path, text):
    doc = fitz.open()
    page = doc.new_page(width=400, height=400)
    page.insert_text((50, 60), text, fontsize=14)
    doc.save(str(path))
    doc.close()


def test_pdf_quality_accepts_text_and_checks_recall(tmp_path):
    path = tmp_path / "valid.pdf"
    _text_pdf(path, "Alpha 123")
    report = inspect_pdf_quality(path, expected_text="Alpha 123")
    assert report.pages == 1
    assert report.text_recall == 1
    assert report.expected_characters == 8
    assert report.clipped_characters == 0
    assert "pages" in report.as_dict()
    assert report.pdf_fonts


def test_pdf_quality_rejects_missing_unicode(tmp_path):
    path = tmp_path / "missing.pdf"
    _text_pdf(path, "Alpha")
    with pytest.raises(ValueError, match="text recall"):
        inspect_pdf_quality(path, expected_text="AlphaExtra")


def test_pdf_quality_detects_off_page_text(tmp_path):
    path = tmp_path / "clipped.pdf"
    doc = fitz.open()
    page = doc.new_page(width=160, height=160)
    page.insert_text((150, 60), "RIGHT", fontsize=24)
    doc.save(str(path))
    doc.close()
    # MuPDF may clip overflow before extraction; either character-count recall
    # or box geometry catches the missing text.
    with pytest.raises(ValueError, match="(text recall|off-page)"):
        inspect_pdf_quality(path, expected_text="RIGHT")


def test_pdf_quality_counts_real_images(tmp_path):
    from io import BytesIO
    image = Image.new("RGB", (20, 20), (100, 20, 30))
    stream = BytesIO()
    image.save(stream, format="PNG")
    path = tmp_path / "image.pdf"
    doc = fitz.open()
    page = doc.new_page(width=200, height=200)
    page.insert_image(fitz.Rect(20, 20, 120, 120), stream=stream.getvalue())
    doc.save(str(path))
    doc.close()
    report = inspect_pdf_quality(path, expected_images=1)
    assert report.image_instances >= 1
    with pytest.raises(ValueError, match="image count"):
        inspect_pdf_quality(path, expected_images=2)


def test_pdf_quality_rejects_out_of_range_threshold(tmp_path):
    path = tmp_path / "valid.pdf"
    _text_pdf(path, "ok")
    with pytest.raises(ValueError, match="min_recall"):
        inspect_pdf_quality(path, min_recall=1.2)


def test_md2pdf_rejects_inplace_conversion_without_backends(tmp_path):
    source = tmp_path / "doc.md"
    source.write_text("# 原文")
    with pytest.raises(ValueError, match="must differ"):
        markdown_to_pdf(str(source), str(source))
    assert source.read_text() == "# 原文"


def test_cli_exposes_quality_configuration():
    output = CliRunner().invoke(cli, ["convert", "md2pdf", "--help"])
    assert output.exit_code == 0
    assert "--font-family" in output.output
    assert "--min-text-recall" in output.output


def _requirements():
    missing = [name for name in ("pandoc", "libreoffice", "fc-match") if not shutil.which(name)]
    if missing:
        pytest.skip("Missing integration backends: " + ", ".join(missing))
    try:
        fonts.choose_cjk_font("中文日本語")
    except (RuntimeError, ValueError) as exc:
        pytest.skip("No installed CJK font: " + str(exc))


@pytest.mark.pdf_integration
def test_real_cjk_pdf_content_and_table_layout(cjk_markdown, tmp_path):
    _requirements()
    output = tmp_path / "cjk.pdf"
    result = markdown_to_pdf(str(cjk_markdown), str(output))
    assert result == str(output)
    with fitz.open(str(output)) as pdf:
        assert pdf.page_count >= 1
        all_text = "".join(page.get_text("text") for page in pdf)
        assert "中文版式测试" in all_text
        assert "日本語" in all_text
        assert "实验数据" in all_text
        assert "样例A" in all_text
        assert sum(len(page.get_image_info()) for page in pdf) >= 1
        assert any(page.get_pixmap().samples for page in pdf)
    report = inspect_pdf_quality(
        output, expected_text="中文版式测试 这里包含中文和日本語 English text remains selectable 实验数据"
    )
    assert report.text_recall >= 0.995
    assert report.clipped_characters == 0
    assert report.replacement_glyphs == 0


@pytest.mark.pdf_integration
def test_missing_pdf_asset_never_replaces_existing_output(tmp_path):
    _requirements()
    source = tmp_path / "notfound.md"
    source.write_text("# 标题\n![image](missing.png)", encoding="utf-8")
    output = tmp_path / "existing.pdf"
    output.write_bytes(b"UNMODIFIED")
    with pytest.raises(FileNotFoundError, match="image"):
        markdown_to_pdf(str(source), str(output))
    assert output.read_bytes() == b"UNMODIFIED"


@pytest.mark.pdf_integration
def test_cli_real_cjk_pdf(cjk_markdown, tmp_path):
    _requirements()
    output = tmp_path / "cli.pdf"
    process = CliRunner().invoke(
        cli, ["convert", "md2pdf", str(cjk_markdown), "-o", str(output)]
    )
    assert process.exit_code == 0, process.output
    assert output.exists()
    with fitz.open(str(output)) as pdf:
        assert "中文版式测试" in pdf[0].get_text()


@pytest.mark.pdf_integration
def test_real_pdf_render_has_nonempty_raster(cjk_markdown, tmp_path):
    _requirements()
    output = tmp_path / "visual.pdf"
    markdown_to_pdf(str(cjk_markdown), str(output))
    with fitz.open(str(output)) as pdf:
        first = pdf[0].get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
        assert first.width >= 500
        assert first.height >= 700
        # RGB pixels must contain actual ink; a blank page alone is invalid.
        assert any(channel < 180 for channel in first.samples[::3])

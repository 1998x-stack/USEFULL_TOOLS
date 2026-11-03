"""End-to-end V0.4-B golden tests against real Pandoc and real OOXML."""

import json
import os
import shutil
import zipfile
from pathlib import Path

import pytest
from click.testing import CliRunner
from docx import Document
from PIL import Image

from devkit.cli import cli
from devkit.convert.doc_convert import convert_document
from devkit.convert.engines import PandocEngine
from devkit.convert.ir import from_pandoc_ast
from devkit.convert.md2docx import markdown_to_docx
from devkit.convert.validate.structure import inspect_docx


@pytest.fixture
def rich_source(tmp_path):
    fixture = Path(__file__).parent / "fixtures" / "conversion_v04b" / "rich.md"
    path = tmp_path / "rich.md"
    path.write_text(fixture.read_text(encoding="utf-8"), encoding="utf-8")
    assets = tmp_path / "assets"
    assets.mkdir()
    Image.new("RGB", (4, 4), (200, 30, 40)).save(assets / "tiny.png")
    return path


@pytest.fixture
def golden_ir(rich_source):
    if not shutil.which("pandoc"):
        pytest.skip("requires actual Pandoc binary")
    return PandocEngine().parse_markdown(rich_source)


def test_document_ir_is_lossless_json(golden_ir):
    ast = golden_ir.to_pandoc_ast()
    assert ast["pandoc-api-version"]
    assert ast["blocks"][0]["t"] == "Header"
    assert json.loads(golden_ir.ast_json) == ast
    assert from_pandoc_ast(ast).ast_json == golden_ir.ast_json


def test_ir_heading_and_paragraph(golden_ir):
    assert golden_ir.feature_count("Header") == 5
    assert golden_ir.blocks[0].kind == "heading"
    assert golden_ir.blocks[0].text == "Document Lab 中文测试"
    assert golden_ir.blocks[0].level == 1
    paragraph = next(block for block in golden_ir.blocks if block.kind == "paragraph")
    assert paragraph.text.startswith("A bold word")
    assert paragraph.source_ref.startswith("blocks[")


def test_ir_preserves_inline_formatting_and_link_targets(golden_ir):
    paragraph = next(block for block in golden_ir.blocks if block.kind == "paragraph")
    strong = [run for run in paragraph.inlines if run.kind == "Strong"]
    emph = [run for run in paragraph.inlines if run.kind == "Emph"]
    links = [run for run in paragraph.inlines if run.kind == "Link"]
    assert len(strong) == len(emph) == len(links) == 1
    assert strong[0].text == "bold"
    assert emph[0].text == "italic"
    assert links[0].target == "https://example.org/info"


def test_ir_nested_bullets_and_numbering(golden_ir):
    bullet = next(block for block in golden_ir.blocks if block.kind == "bullet_list")
    ordered = next(block for block in golden_ir.blocks if block.kind == "ordered_list")
    assert len(bullet.children) == 2
    assert len(ordered.children) == 2
    assert any(nested.kind == "bullet_list" for nested in bullet.children[0].children)
    assert golden_ir.feature_count("BulletList") == 2
    assert golden_ir.feature_count("OrderedList") == 1


def test_ir_table_cells_remain_structured(golden_ir):
    table = next(block for block in golden_ir.blocks if block.kind == "table")
    assert golden_ir.feature_count("Table") == 1
    assert len(table.children) == 3
    assert all(row.kind == "table_row" and len(row.children) == 2 for row in table.children)
    assert all(cell.kind == "table_cell" for row in table.children for cell in row.children)
    assert table.children[1].children[0].children[0].text == "Alpha"
    assert table.children[2].children[1].children[0].text == "92"


def test_ir_embedded_image_reference(golden_ir):
    assert golden_ir.feature_count("Image") == 1
    assert golden_ir.image_sources == ("assets/tiny.png",)


def test_real_docx_golden_structure(rich_source, tmp_path):
    if not shutil.which("pandoc"):
        pytest.skip("requires actual Pandoc binary")
    output = tmp_path / "document.docx"
    assert markdown_to_docx(str(rich_source), str(output)) == str(output)
    word = Document(str(output))
    assert len(word.tables) == 1
    assert len(word.inline_shapes) == 1
    assert word.tables[0].cell(0, 0).text == "Model"
    assert word.tables[0].cell(1, 0).text == "Alpha"
    assert word.tables[0].cell(2, 1).text == "92"
    styles = [p.style.name for p in word.paragraphs]
    assert any(name.startswith("Heading 1") for name in styles)
    all_runs = [r for p in word.paragraphs for r in p.runs]
    assert any(r.bold and "bold" in r.text for r in all_runs)
    assert any(r.italic and "italic" in r.text for r in all_runs)
    inspected = inspect_docx(output)
    assert inspected.headings >= 5
    assert inspected.hyperlinks >= 1
    assert inspected.images >= 1
    assert inspected.tables == 1
    assert inspected.list_items >= 4
    with zipfile.ZipFile(output) as archive:
        relationships = archive.read("word/_rels/document.xml.rels").decode()
        assert "https://example.org/info" in relationships


def test_cli_md2docx_uses_same_engine(rich_source, tmp_path):
    if not shutil.which("pandoc"):
        pytest.skip("requires actual Pandoc binary")
    output = tmp_path / "from-cli.docx"
    result = CliRunner().invoke(cli, ["convert", "md2docx", str(rich_source), "-o", str(output)])
    assert result.exit_code == 0, result.output
    assert len(Document(str(output)).tables) == 1


def test_cli_generic_doc_uses_same_engine(rich_source, tmp_path):
    if not shutil.which("pandoc"):
        pytest.skip("requires actual Pandoc binary")
    output = tmp_path / "generic.docx"
    result = CliRunner().invoke(
        cli, ["convert", "doc", str(rich_source), "--to", "docx", "-o", str(output)]
    )
    assert result.exit_code == 0, result.output
    assert len(Document(str(output)).inline_shapes) == 1


def test_custom_reference_doc_keeps_document_valid(rich_source, tmp_path):
    if not shutil.which("pandoc"):
        pytest.skip("requires actual Pandoc binary")
    reference = tmp_path / "reference.docx"
    markdown_to_docx(str(rich_source), str(reference))
    output = tmp_path / "styled.docx"
    assert convert_document(str(rich_source), "docx", str(output), reference_doc=str(reference)) == str(output)
    assert len(Document(str(output)).tables) == 1


def test_remote_image_refused_without_output(tmp_path):
    source = tmp_path / "remote.md"
    source.write_text("![remote](https://example.org/photo.png)", encoding="utf-8")
    if not shutil.which("pandoc"):
        pytest.skip("requires actual Pandoc binary")
    output = tmp_path / "remote.docx"
    with pytest.raises(ValueError, match="external"):
        markdown_to_docx(str(source), str(output))
    assert not output.exists()


def test_missing_image_preserves_existing_output(tmp_path):
    if not shutil.which("pandoc"):
        pytest.skip("requires actual Pandoc binary")
    source = tmp_path / "missing.md"
    source.write_text("![missing](assets/missing.png)", encoding="utf-8")
    output = tmp_path / "existing.docx"
    output.write_bytes(b"ORIGINAL")
    with pytest.raises(FileNotFoundError, match="image"):
        markdown_to_docx(str(source), str(output))
    assert output.read_bytes() == b"ORIGINAL"


def test_media_outside_root_refused(tmp_path):
    if not shutil.which("pandoc"):
        pytest.skip("requires actual Pandoc binary")
    source = tmp_path / "sub" / "input.md"
    source.parent.mkdir()
    (tmp_path / "private.png").write_bytes(b"secret")
    source.write_text("![escape](../private.png)", encoding="utf-8")
    with pytest.raises(ValueError, match="escapes"):
        markdown_to_docx(str(source))


def test_same_input_output_blocked_before_runner(tmp_path):
    source = tmp_path / "in.md"
    source.write_text("# Header")
    with pytest.raises(ValueError, match="must differ"):
        markdown_to_docx(str(source), str(source))
    assert source.read_text() == "# Header"


def test_invalid_pandoc_ast_is_rejected():
    with pytest.raises(ValueError, match="Pandoc"):
        from_pandoc_ast({"blocks": [], "meta": {}})
    with pytest.raises(ValueError, match="blocks"):
        from_pandoc_ast({"pandoc-api-version": [1, 23, 1], "meta": {}, "blocks": "invalid"})


def test_pandoc_missing_is_explicit_error(monkeypatch):
    import devkit.convert.engines.pandoc as engine_module
    monkeypatch.setattr(engine_module.shutil, "which", lambda _: None)
    with pytest.raises(FileNotFoundError, match="Pandoc binary"):
        PandocEngine()


def test_image_symlink_escape_blocked(tmp_path):
    if not shutil.which("pandoc"):
        pytest.skip("requires actual Pandoc binary")
    source = tmp_path / "doc" / "in.md"
    source.parent.mkdir()
    external = tmp_path / "external.png"
    external.write_bytes(b"unsafe")
    try:
        os.symlink(external, source.parent / "photo.png")
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unsupported")
    source.write_text("![escapes](photo.png)")
    with pytest.raises(ValueError, match="escapes"):
        markdown_to_docx(str(source))


def test_reference_template_cannot_be_overwritten(rich_source, tmp_path):
    if not shutil.which("pandoc"):
        pytest.skip("requires actual Pandoc binary")
    template = tmp_path / "reference.docx"
    markdown_to_docx(str(rich_source), str(template))
    previous = template.read_bytes()
    with pytest.raises(ValueError, match="must differ"):
        markdown_to_docx(str(rich_source), str(template), reference_doc=str(template))
    assert template.read_bytes() == previous

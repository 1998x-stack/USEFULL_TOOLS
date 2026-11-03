"""V0.3: data fidelity, validation, streaming, and failure recovery."""

import csv
import json
import os

import pytest
from click.testing import CliRunner

from devkit.cli import cli
from devkit.data.csv_utils import csv_to_json, json_to_csv, merge_csvs, split_csv
from devkit.data.json_utils import flatten_json, json_query, merge_jsonl, unflatten_json


def _csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as stream:
        csv.writer(stream).writerows(rows)


def test_merge_rejects_different_schema_without_modifying_output(tmp_path):
    a, b, target = [tmp_path / name for name in ("a.csv", "b.csv", "out.csv")]
    _csv(a, [["name", "age"], ["Alice", "30"]])
    _csv(b, [["age", "name"], ["22", "Bob"]])
    target.write_text("ORIGINAL")
    with pytest.raises(ValueError, match="header mismatch"):
        merge_csvs([str(a), str(b)], str(target))
    assert target.read_text() == "ORIGINAL"
    assert not list(tmp_path.glob(".devkit-write-*"))


def test_merge_rejects_malformed_row_without_output(tmp_path):
    source, target = tmp_path / "bad.csv", tmp_path / "out.csv"
    _csv(source, [["a", "b"], ["good", "row"], ["broken"]])
    with pytest.raises(ValueError, match="column count mismatch"):
        merge_csvs([str(source)], str(target))
    assert not target.exists()


@pytest.mark.parametrize("header", [["x", "x"], ["x", " "]])
def test_csv_rejects_bad_column_names(tmp_path, header):
    path = tmp_path / "bad.csv"
    _csv(path, [header, ["1", "2"]])
    with pytest.raises(ValueError, match="header"):
        csv_to_json(str(path), str(tmp_path / "result.json"))


def test_merge_bom_multiline_and_unicode(tmp_path):
    a, b, dest = [tmp_path / name for name in ("a.csv", "b.csv", "out.csv")]
    a.write_bytes("\ufeffname,notes\n你好,\"a\nb\"\n".encode("utf-8"))
    _csv(b, [["name", "notes"], ["World", "fine"]])
    merge_csvs([str(a), str(b)], str(dest))
    with dest.open(newline="", encoding="utf-8") as stream:
        assert list(csv.reader(stream)) == [
            ["name", "notes"], ["你好", "a\nb"], ["World", "fine"]
        ]


def test_merge_refuses_same_input_output(tmp_path):
    a = tmp_path / "a.csv"
    original = "name\nAlice\n"
    a.write_text(original)
    with pytest.raises(ValueError, match="Output must differ"):
        merge_csvs([str(a)], str(a))
    assert a.read_text() == original


def test_merge_refuses_hardlink_output_alias(tmp_path):
    a, linked = tmp_path / "a.csv", tmp_path / "alias.csv"
    _csv(a, [["name"], ["Alice"]])
    try:
        os.link(a, linked)
    except OSError:
        pytest.skip("hardlinks unsupported")
    with pytest.raises(ValueError, match="Output must differ"):
        merge_csvs([str(a)], str(linked))


@pytest.mark.parametrize("rows", [0, -2])
def test_split_rejects_nonpositive_rows(tmp_path, rows):
    original = tmp_path / "data.csv"
    _csv(original, [["a"], ["1"]])
    with pytest.raises(ValueError, match="positive"):
        split_csv(str(original), rows, str(tmp_path / "parts"))
    assert not (tmp_path / "parts").exists()


def test_split_preserves_existing_part_files(tmp_path):
    source, dest = tmp_path / "data.csv", tmp_path / "parts"
    _csv(source, [["a"], ["1"], ["2"]])
    dest.mkdir()
    (dest / "part_001.csv").write_text("KEEP")
    with pytest.raises(FileExistsError):
        split_csv(str(source), 1, str(dest))
    assert (dest / "part_001.csv").read_text() == "KEEP"
    assert not (dest / "part_002.csv").exists()
    assert not list(dest.glob(".devkit-split-*"))


def test_split_invalid_row_never_publishes_parts(tmp_path):
    source, dest = tmp_path / "data.csv", tmp_path / "parts"
    _csv(source, [["a", "b"], ["1", "2"], ["3"]])
    with pytest.raises(ValueError, match="column count mismatch"):
        split_csv(str(source), 1, str(dest))
    assert list(dest.iterdir()) == []


def test_split_streams_and_preserves_multiline_rows(tmp_path):
    source, dest = tmp_path / "data.csv", tmp_path / "parts"
    _csv(source, [["a", "b"], ["1", "hello\nworld"], ["2", "ok"], ["3", "ok"]])
    outputs = split_csv(str(source), 2, str(dest))
    assert len(outputs) == 2
    with open(outputs[0], newline="", encoding="utf-8") as f:
        assert list(csv.reader(f)) == [["a", "b"], ["1", "hello\nworld"], ["2", "ok"]]


def test_csv_to_json_rejects_invalid_row_preserves_existing_output(tmp_path):
    source, output = tmp_path / "data.csv", tmp_path / "out.json"
    _csv(source, [["a", "b"], ["1", "2"], ["3"]])
    output.write_text("KEEP")
    with pytest.raises(ValueError, match="column count mismatch"):
        csv_to_json(str(source), str(output))
    assert output.read_text() == "KEEP"


def test_csv_to_json_handles_long_stream(tmp_path):
    source, output = tmp_path / "data.csv", tmp_path / "out.json"
    _csv(source, [["name", "comment"]] + [[f"user{i}", f"note{i}"] for i in range(2500)])
    csv_to_json(str(source), str(output))
    content = json.loads(output.read_text())
    assert len(content) == 2500
    assert content[2499]["name"] == "user2499"


def test_json_to_csv_streams_large_elements_across_chunks(tmp_path):
    source, output = tmp_path / "in.json", tmp_path / "out.csv"
    source.write_text(json.dumps([{"name": "A" * 100000, "id": 1}, {"id": 2, "name": "B"}]))
    json_to_csv(str(source), str(output))
    with output.open(newline="") as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["name", "id"]
    assert rows[1] == ["A" * 100000, "1"]
    assert rows[2] == ["B", "2"]


def test_json_to_csv_rejects_schema_change_preserves_output(tmp_path):
    source, output = tmp_path / "in.json", tmp_path / "out.csv"
    source.write_text('[{"a":1},{"b":2}]')
    output.write_text("OLD")
    with pytest.raises(ValueError, match="different field schema"):
        json_to_csv(str(source), str(output))
    assert output.read_text() == "OLD"


def test_json_to_csv_nested_values_use_json_encoding(tmp_path):
    source, output = tmp_path / "in.json", tmp_path / "out.csv"
    source.write_text('[{"id":1,"meta":{"k":1}},{"id":2,"meta":[true,null]}]')
    json_to_csv(str(source), str(output))
    with output.open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert json.loads(rows[0]["meta"]) == {"k": 1}
    assert json.loads(rows[1]["meta"]) == [True, None]


def test_json_to_csv_rejects_duplicate_keys(tmp_path):
    source, output = tmp_path / "in.json", tmp_path / "out.csv"
    source.write_text('[{"x":1,"x":2}]')
    with pytest.raises(ValueError, match="Duplicate JSON key"):
        json_to_csv(str(source), str(output))
    assert not output.exists()


def test_json_to_csv_rejects_empty_and_invalid_arrays(tmp_path):
    source, output = tmp_path / "in.json", tmp_path / "out.csv"
    output.write_text("OLD")
    for content in ("[]", '{"a": 1}', '[{"a":1},]', '[{"a":1}]{ }', '[1]'):
        source.write_text(content)
        with pytest.raises(ValueError):
            json_to_csv(str(source), str(output))
        assert output.read_text() == "OLD"


def test_jsonl_invalid_line_preserves_output(tmp_path):
    a, b, out = [tmp_path / x for x in ("a.jsonl", "b.jsonl", "merged.jsonl")]
    a.write_text('{"ok":1}\n')
    b.write_text('{"ok":2}\n{not valid}\n')
    out.write_text("SAFE")
    with pytest.raises(ValueError, match="line 2"):
        merge_jsonl([str(a), str(b)], str(out))
    assert out.read_text() == "SAFE"


def test_jsonl_merge_preserves_valid_records_and_skips_blank_lines(tmp_path):
    a, out = tmp_path / "a.jsonl", tmp_path / "merged.jsonl"
    a.write_text('{"x":1}\n\n[1,2]\n')
    merge_jsonl([str(a)], str(out))
    assert out.read_text().splitlines() == ['{"x":1}', '[1,2]']


def test_jsonl_refuses_input_as_output(tmp_path):
    a = tmp_path / "a.jsonl"
    a.write_text('{"x":1}\n')
    with pytest.raises(ValueError, match="Output must differ"):
        merge_jsonl([str(a)], str(a))
    assert a.read_text() == '{"x":1}\n'


def test_json_flatten_escapes_colliding_keys():
    obj = {"a": {"b": 1}, "a.b": 2, "back\\slash": {"x": 3}}
    flattened = flatten_json(obj)
    assert flattened["a.b"] == 1
    assert flattened["a\\.b"] == 2
    assert flattened["back\\\\slash.x"] == 3
    assert unflatten_json(flattened) == obj
    assert json_query(obj, "a\\.b") == 2


def test_json_flatten_preserves_empty_objects_and_empty_keys():
    obj = {"": {"a.b": {}}, "empty": {}, "key": {"": 3}}
    assert unflatten_json(flatten_json(obj)) == obj


def test_json_flatten_round_trip_custom_separator():
    obj = {"a/b": {"slash\\key": [1, 2]}, "a": {"b": 5}}
    flattened = flatten_json(obj, separator="/")
    assert unflatten_json(flattened, separator="/") == obj
    assert json_query(obj, "a\\/b/slash\\\\key", separator="/") == [1, 2]


@pytest.mark.parametrize("bad", [{"a": 1, "a.b": 2}, {"a.b": 2, "a": 1}, {"a": {}, "a.b": 2}])
def test_unflatten_rejects_conflicting_paths(bad):
    with pytest.raises(ValueError, match="Conflicting"):
        unflatten_json(bad)


@pytest.mark.parametrize("bad", ["a\\q", "a\\"])
def test_unflatten_rejects_invalid_path_escapes(bad):
    with pytest.raises(ValueError, match="escape"):
        unflatten_json({bad: 1})


def test_cli_flatten_refuses_inplace_output(tmp_path):
    path = tmp_path / "input.json"
    original = '{"a":{"b":1}}'
    path.write_text(original)
    result = CliRunner().invoke(cli, ["data", "json-flatten", str(path), "-o", str(path)])
    assert result.exit_code != 0
    assert "Output must differ" in result.output
    assert path.read_text() == original


def test_cli_csv_merge_reports_schema_error(tmp_path):
    a, b, output = tmp_path / "a.csv", tmp_path / "b.csv", tmp_path / "out.csv"
    _csv(a, [["a", "b"], ["1", "2"]])
    _csv(b, [["b", "a"], ["3", "4"]])
    result = CliRunner().invoke(cli, ["data", "csv-merge", str(a), str(b), "-o", str(output)])
    assert result.exit_code != 0
    assert "header mismatch" in result.output
    assert not output.exists()


def test_excel_convert_atomic_and_select_sheet(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    from devkit.data.excel2csv import excel_to_csv
    book = openpyxl.Workbook()
    book.active.title = "Raw"
    second = book.create_sheet("Named")
    second.append(["name", "value"])
    second.append(["测试", 3])
    source, output = tmp_path / "table.xlsx", tmp_path / "table.csv"
    book.save(source)
    excel_to_csv(str(source), str(output), sheet="Named")
    with output.open(newline="") as f:
        assert list(csv.reader(f)) == [["name", "value"], ["测试", "3"]]
    output.write_text("OLD")
    with pytest.raises(KeyError):
        excel_to_csv(str(source), str(output), sheet="NoSuchSheet")
    assert output.read_text() == "OLD"


def test_atomic_outputs_replace_after_success(tmp_path):
    a, out = tmp_path / "a.csv", tmp_path / "out.csv"
    _csv(a, [["name"], ["A"]])
    out.write_text("OLD")
    merge_csvs([str(a)], str(out))
    with out.open(newline="") as f:
        assert list(csv.reader(f)) == [["name"], ["A"]]
    assert not list(tmp_path.glob(".devkit-write-*"))



@pytest.mark.parametrize("record", ['{"x":NaN}', '{"x":Infinity}', '{"x":1,"x":2}'])
def test_jsonl_rejects_nonstandard_or_duplicate_json(tmp_path, record):
    src, out = tmp_path / "invalid.jsonl", tmp_path / "out.jsonl"
    src.write_text(record + "\n")
    with pytest.raises(ValueError):
        merge_jsonl([str(src)], str(out))
    assert not out.exists()


def test_json_to_csv_rejects_nonfinite_json(tmp_path):
    src, out = tmp_path / "invalid.json", tmp_path / "out.csv"
    src.write_text('[{"x": NaN}]')
    with pytest.raises(ValueError, match="Non-standard"):
        json_to_csv(str(src), str(out))
    assert not out.exists()


def test_cli_flatten_rejects_duplicate_json_keys(tmp_path):
    src, out = tmp_path / "bad.json", tmp_path / "out.json"
    src.write_text('{"x":1,"x":2}')
    result = CliRunner().invoke(cli, ["data", "json-flatten", str(src), "-o", str(out)])
    assert result.exit_code != 0
    assert "Duplicate JSON key" in result.output
    assert not out.exists()

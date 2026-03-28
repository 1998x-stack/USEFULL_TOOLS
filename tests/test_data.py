"""Tests for data processing tools."""

import csv
import json
import os

from devkit.data.json_utils import flatten_json, unflatten_json, json_query, merge_jsonl
from devkit.data.csv_utils import merge_csvs, split_csv, csv_to_json, json_to_csv


def test_flatten_json():
    data = {"a": {"b": {"c": 1}}, "d": 2}
    result = flatten_json(data)
    assert result == {"a.b.c": 1, "d": 2}


def test_flatten_json_custom_separator():
    data = {"a": {"b": 1}}
    result = flatten_json(data, separator="/")
    assert result == {"a/b": 1}


def test_unflatten_json():
    data = {"a.b.c": 1, "a.b.d": 2, "e": 3}
    result = unflatten_json(data)
    assert result == {"a": {"b": {"c": 1, "d": 2}}, "e": 3}


def test_json_query():
    data = {"a": {"b": [1, 2, 3]}}
    assert json_query(data, "a.b") == [1, 2, 3]
    assert json_query(data, "a") == {"b": [1, 2, 3]}
    assert json_query(data, "x.y") is None


def test_merge_jsonl(tmp_path):
    f1 = tmp_path / "a.jsonl"
    f2 = tmp_path / "b.jsonl"
    f1.write_text('{"x": 1}\n{"x": 2}\n')
    f2.write_text('{"x": 3}\n')
    out = str(tmp_path / "merged.jsonl")
    merge_jsonl([str(f1), str(f2)], out)
    with open(out) as f:
        lines = f.readlines()
    assert len(lines) == 3


def test_merge_csvs(tmp_path):
    for i, rows in enumerate([
        [["name", "age"], ["Alice", "30"]],
        [["name", "age"], ["Bob", "25"]],
    ]):
        f = tmp_path / f"f{i}.csv"
        with open(f, "w", newline="") as csvfile:
            csv.writer(csvfile).writerows(rows)
    out = str(tmp_path / "merged.csv")
    merge_csvs([str(tmp_path / "f0.csv"), str(tmp_path / "f1.csv")], out)
    with open(out) as f:
        reader = csv.reader(f)
        rows = list(reader)
    assert len(rows) == 3


def test_split_csv(tmp_path):
    f = tmp_path / "big.csv"
    with open(f, "w", newline="") as csvfile:
        w = csv.writer(csvfile)
        w.writerow(["id", "value"])
        for i in range(10):
            w.writerow([i, f"val_{i}"])
    out_dir = str(tmp_path / "splits")
    split_csv(str(f), rows_per_file=3, output_dir=out_dir)
    split_files = os.listdir(out_dir)
    assert len(split_files) == 4


def test_csv_to_json(tmp_path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("name,age\nAlice,30\nBob,25\n")
    out = str(tmp_path / "data.json")
    csv_to_json(str(csv_file), out)
    with open(out) as f:
        data = json.load(f)
    assert len(data) == 2
    assert data[0]["name"] == "Alice"


def test_json_to_csv(tmp_path):
    json_file = tmp_path / "data.json"
    json_file.write_text('[{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]')
    out = str(tmp_path / "data.csv")
    json_to_csv(str(json_file), out)
    with open(out) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) == 2

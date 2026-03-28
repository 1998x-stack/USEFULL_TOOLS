"""Tests for file management tools."""

import os

from devkit.files.dedup import find_duplicates
from devkit.files.search_log import search_file
from devkit.files.extract_code import extract_code_files
from devkit.files.batch_rename import batch_rename


def test_find_duplicates(tmp_path):
    (tmp_path / "file.txt").write_text("content")
    (tmp_path / "file (1).txt").write_text("duplicate")
    dups = find_duplicates(str(tmp_path), extensions=["*.txt"])
    assert len(dups) == 1
    assert "file (1).txt" in dups[0]


def test_find_duplicates_no_dupes(tmp_path):
    (tmp_path / "file.txt").write_text("content")
    dups = find_duplicates(str(tmp_path), extensions=["*.txt"])
    assert len(dups) == 0


def test_search_file(tmp_path):
    log_file = tmp_path / "test.log"
    log_file.write_text("line 1\nline 2\nerror found here\nline 4\n")
    results = search_file(str(log_file), "error")
    assert len(results) > 0
    assert any("error found here" in r["line"] for r in results)


def test_search_file_not_found():
    results = search_file("/nonexistent/file.log", "test")
    assert results == []


def test_extract_code_files(tmp_path):
    (tmp_path / "app.py").write_text("print('hello')")
    (tmp_path / "style.css").write_text("body { color: red; }")
    (tmp_path / "notes.txt").write_text("not code")
    result = extract_code_files(str(tmp_path), extensions=["py", "css"])
    assert "app.py" in result
    assert "print('hello')" in result
    assert "notes.txt" not in result


def test_batch_rename_dry_run(tmp_path):
    (tmp_path / "photo1.jpg").write_text("")
    (tmp_path / "photo2.jpg").write_text("")
    renames = batch_rename(str(tmp_path), pattern="img_{n:03d}.jpg", dry_run=True)
    assert len(renames) == 2
    assert renames[0][1].endswith("img_001.jpg")
    assert (tmp_path / "photo1.jpg").exists()


def test_batch_rename_execute(tmp_path):
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    renames = batch_rename(str(tmp_path), pattern="file_{n:02d}.txt", dry_run=False)
    assert len(renames) == 2
    assert (tmp_path / "file_01.txt").exists()
    assert (tmp_path / "file_02.txt").exists()
